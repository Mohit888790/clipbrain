# Database Schema Design

This document explains the design decisions and rationale behind the ClipBrain database schema.

## Overview

The schema is designed to support:
- Asynchronous video processing pipeline with status tracking
- Hybrid search combining vector similarity and full-text search
- Efficient storage and retrieval of time-segmented transcript chunks
- AI-generated structured notes with flexible JSON fields
- User-created collections for organizing videos

## Tables

### videos

**Purpose**: Central table storing video metadata and processing status.

**Key Design Decisions**:
- `canonical_url_hash`: Ensures deduplication by hashing normalized URLs
- `status` enum: Tracks pipeline progress (queued → processing → done/failed)
- `current_stage`: Provides granular visibility into which pipeline stage is running
- `platform` enum: Restricts to supported platforms for validation
- `storage_path`: References Supabase Storage location for downloaded media
- `fail_reason`: Stores error codes for debugging and user feedback

**Indexes**:
- `idx_videos_status`: Fast filtering by processing status
- `idx_videos_created`: Chronological ordering for "recent videos" view
- `idx_videos_canonical`: Ensures fast duplicate detection
- `idx_videos_title_trgm`: Enables fuzzy title search with trigrams

**Constraints**:
- `canonical_url_hash` UNIQUE: Prevents duplicate ingestion
- `platform` CHECK: Validates platform is supported
- `status` CHECK: Ensures valid status values

### transcripts

**Purpose**: Stores full transcript text for each video.

**Key Design Decisions**:
- Separate table from `videos` to keep video metadata lightweight
- `full_text` stored as TEXT for unlimited length
- One-to-one relationship with `videos` (enforced at application level)

**Indexes**:
- `idx_transcripts_video`: Fast lookup by video_id
- `idx_transcripts_fulltext`: GIN index for PostgreSQL full-text search using tsvector

**Why Separate Table**:
- Transcripts can be very large (10k+ words)
- Separating allows efficient queries on video metadata without loading transcript
- Enables independent caching strategies

### transcript_chunks

**Purpose**: Time-segmented chunks of transcript with embeddings for semantic search.

**Key Design Decisions**:
- `start_ms` / `end_ms`: Millisecond precision for accurate timestamp linking
- `text_hash`: SHA-256 hash of normalized text for embedding cache lookup
- `embedding`: 768-dimensional vector (Gemini text-embedding-004 dimension)
- Multiple chunks per video for granular search results

**Indexes**:
- `idx_chunks_video`: Fast retrieval of all chunks for a video
- `idx_chunks_embedding`: IVFFLAT index for approximate nearest neighbor search
- `idx_chunks_text_hash`: Fast cache lookup to avoid re-generating embeddings

**IVFFLAT Index Configuration**:
- `lists = 100`: Suitable for ~10k chunks (rule of thumb: sqrt(rows))
- `vector_cosine_ops`: Cosine similarity for normalized embeddings
- Trade-off: Faster search with slight accuracy loss vs exact KNN

**Why Chunking**:
- Enables timestamp-specific search results
- Smaller chunks = more precise semantic matching
- 10-15 second windows balance context vs granularity

### notes

**Purpose**: AI-generated structured notes extracted from video content.

**Key Design Decisions**:
- `keywords` as TEXT[]: Native PostgreSQL array for efficient tag filtering
- `chapters`, `insights`, `steps`, `quotes`, `entities` as JSONB: Flexible schema for complex structures
- `notes_raw_text`: Fallback storage if JSON parsing fails
- One-to-one relationship with `videos`

**Indexes**:
- `idx_notes_video`: Fast lookup by video_id
- `idx_notes_keywords`: GIN index for array overlap queries (tag filtering)

**JSONB Structure Examples**:
```json
{
  "chapters": [
    {"title": "Introduction", "start_ms": 0},
    {"title": "Main Topic", "start_ms": 45000}
  ],
  "insights": [
    "Key insight 1",
    "Key insight 2"
  ],
  "quotes": [
    {"text": "Important quote", "start_ms": 12000}
  ],
  "entities": {
    "people": ["John Doe"],
    "tools": ["Python", "FastAPI"],
    "urls": ["https://example.com"]
  }
}
```

**Why JSONB**:
- Flexible schema for evolving AI output formats
- Efficient indexing and querying with GIN indexes
- Native JSON operators for filtering and extraction

### collections

**Purpose**: User-created collections for organizing videos.

**Key Design Decisions**:
- `name` UNIQUE: Prevents duplicate collection names
- Simple structure: just id and name
- Relationship to videos via junction table

**Why Separate Collections Table**:
- Enables many-to-many relationship (video can be in multiple collections)
- Allows collection-level metadata (creation date, description in future)
- Efficient collection listing without loading video data

### collection_items

**Purpose**: Junction table linking videos to collections (many-to-many).

**Key Design Decisions**:
- Composite primary key: `(collection_id, video_id)`
- `added_at`: Tracks when video was added to collection
- Cascade deletes: Removing collection or video cleans up mappings

**Indexes**:
- `idx_collection_items_video`: Fast lookup of collections containing a video
- `idx_collection_items_collection`: Fast lookup of videos in a collection

**Why Junction Table**:
- Standard pattern for many-to-many relationships
- Allows videos in multiple collections
- Enables efficient filtering by collection

## Extensions

### pgvector

**Purpose**: Enables vector similarity search for semantic search.

**Key Features**:
- VECTOR data type for storing embeddings
- IVFFLAT index for approximate nearest neighbor search
- Cosine, L2, and inner product distance operators

**Usage in ClipBrain**:
```sql
-- Find similar chunks
SELECT * FROM transcript_chunks
ORDER BY embedding <=> query_embedding
LIMIT 50;
```

### pg_trgm

**Purpose**: Enables fuzzy text matching using trigrams.

**Key Features**:
- GIN indexes for trigram matching
- Similarity operators for fuzzy search
- Useful for typo-tolerant title search

**Usage in ClipBrain**:
```sql
-- Fuzzy title search
SELECT * FROM videos
WHERE title % 'search query'
ORDER BY similarity(title, 'search query') DESC;
```

## Indexing Strategy

### Index Types Used

1. **B-tree** (default): Foreign keys, timestamps, status fields
2. **GIN**: Full-text search, array fields, JSONB fields
3. **IVFFLAT**: Vector similarity search
4. **GIN trigram**: Fuzzy text matching

### Index Selection Rationale

**Why IVFFLAT for embeddings?**
- Approximate search is acceptable for semantic search
- 10-100x faster than exact KNN for large datasets
- Accuracy loss is minimal (<5%) with proper tuning

**Why GIN for full-text?**
- Optimized for tsvector queries
- Handles complex text search operators (AND, OR, phrase)
- Faster than trigram for exact word matching

**Why trigram for titles?**
- Enables typo-tolerant search
- Useful for user-entered queries with spelling errors
- Complements exact full-text search

## Performance Considerations

### Query Optimization

**Hybrid Search Strategy**:
1. Vector search: LIMIT 50 (fast approximate)
2. Full-text search: LIMIT 50 (GIN index)
3. Merge and re-rank in application layer
4. Target: <1.5s total query time

**Chunking Strategy**:
- 10-15 second chunks balance:
  - Context: Enough words for semantic meaning
  - Granularity: Precise timestamp results
  - Performance: Manageable number of chunks per video

**Embedding Cache**:
- `text_hash` index enables O(1) cache lookup
- Avoids re-generating embeddings for duplicate text
- Critical for cost control (Gemini API quotas)

### Scaling Considerations

**Current Design (Free Tier)**:
- Supports ~1000 videos (500 MB database)
- ~50k transcript chunks (with embeddings)
- Search latency <1.5s with proper indexes

**Future Scaling (Beyond Free Tier)**:
- Increase IVFFLAT lists parameter as data grows
- Consider partitioning `transcript_chunks` by video_id
- Add read replicas for search queries
- Implement query result caching (Redis)

## Data Integrity

### Foreign Key Constraints

All relationships use `ON DELETE CASCADE`:
- Deleting a video removes transcripts, chunks, notes, and collection mappings
- Deleting a collection removes collection_items mappings
- Ensures no orphaned data

### Check Constraints

- `platform` enum: Validates supported platforms
- `status` enum: Ensures valid processing states
- `current_stage` enum: Validates pipeline stages

### Unique Constraints

- `canonical_url_hash`: Prevents duplicate video ingestion
- `collection.name`: Prevents duplicate collection names
- Composite PK on `collection_items`: Prevents duplicate mappings

## Backup and Recovery

### Supabase Automatic Backups

- Daily backups (free tier)
- Point-in-time recovery (paid tiers)
- Manual backup via SQL dump

### Export Strategy

- Application-level export via `/export` endpoint
- Includes JSON data + media files from Storage
- User-initiated full data export

### Disaster Recovery

1. Restore database from Supabase backup
2. Restore Storage files from Supabase backup
3. Re-run migrations if schema changes
4. Verify data integrity with verification script

## Migration Strategy

### Initial Setup

1. Run `001_initial_schema.sql`: Create tables and indexes
2. Run `002_storage_setup.sql`: Configure Storage bucket and policies

### Future Migrations

**Adding Columns**:
```sql
ALTER TABLE videos ADD COLUMN new_field TEXT;
```

**Adding Indexes**:
```sql
CREATE INDEX CONCURRENTLY idx_new_field ON videos(new_field);
```

**Modifying Constraints**:
```sql
ALTER TABLE videos DROP CONSTRAINT videos_platform_check;
ALTER TABLE videos ADD CONSTRAINT videos_platform_check 
  CHECK (platform IN ('youtube', 'instagram', 'tiktok', 'facebook', 'new_platform'));
```

### Best Practices

- Use `CREATE INDEX CONCURRENTLY` to avoid locking
- Test migrations on staging environment first
- Keep migration files numbered and sequential
- Document breaking changes in migration comments

## Security

### Row-Level Security (RLS)

**Current Design**: RLS disabled (no-auth model)
- All access via service_role key
- Security by obscurity (unlisted URL)
- Optional IP allow-list at reverse proxy

**Future Enhancement**: Enable RLS for multi-user
```sql
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own videos" ON videos
  FOR SELECT USING (user_id = auth.uid());
```

### Storage Policies

**Current Design**: Service role only
- Backend generates signed URLs with short TTL
- Frontend never accesses Storage directly
- Prevents unauthorized access to media files

### API Key Security

- Service role key stored server-side only
- Never exposed to frontend
- Rotate keys if compromised

## Monitoring

### Key Metrics to Track

1. **Database Size**: Monitor against free tier limit (500 MB)
2. **Query Performance**: Track slow queries (>1s)
3. **Index Usage**: Verify indexes are being used
4. **Connection Pool**: Monitor active connections
5. **Storage Usage**: Track media file growth

### Useful Queries

**Database Size**:
```sql
SELECT pg_size_pretty(pg_database_size(current_database()));
```

**Table Sizes**:
```sql
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Index Usage**:
```sql
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

**Slow Queries** (enable pg_stat_statements):
```sql
SELECT 
  query,
  calls,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Troubleshooting

### Common Issues

**Slow Vector Search**:
- Check IVFFLAT index exists: `\d transcript_chunks`
- Tune lists parameter based on data size
- Consider increasing lists for >10k chunks

**Full-Text Search Not Working**:
- Verify GIN index on tsvector: `\d transcripts`
- Check query uses `to_tsquery()` correctly
- Ensure text is properly tokenized

**Duplicate Videos**:
- Check `canonical_url_hash` is being set correctly
- Verify URL normalization logic
- Query for duplicates: `SELECT canonical_url_hash, COUNT(*) FROM videos GROUP BY canonical_url_hash HAVING COUNT(*) > 1;`

**Storage Upload Failures**:
- Verify bucket exists: Check Storage dashboard
- Check policies: `SELECT * FROM storage.policies WHERE bucket_id = 'videos';`
- Ensure using service_role key, not anon key

## References

- [Supabase Documentation](https://supabase.com/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [PostgreSQL Trigram Extension](https://www.postgresql.org/docs/current/pgtrgm.html)
