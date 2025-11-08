# Database Setup Guide

This directory contains the database schema and migration files for ClipBrain.

## Prerequisites

1. **Supabase Account**: Sign up at https://supabase.com
2. **Upstash Account**: Sign up at https://upstash.com

## Setup Instructions

### 1. Supabase Setup

#### Create a New Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in project details:
   - Name: `clipbrain` (or your preferred name)
   - Database Password: Generate a strong password and save it
   - Region: Choose closest to your location
4. Wait for project to be provisioned (2-3 minutes)

#### Enable pgvector Extension

1. In your Supabase project dashboard, go to **Database** → **Extensions**
2. Search for `vector` and enable it
3. Alternatively, run in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

#### Run Migrations

1. Go to **SQL Editor** in your Supabase dashboard
2. Create a new query
3. Copy and paste the contents of `migrations/001_initial_schema.sql`
4. Click "Run" to execute
5. Repeat for `migrations/002_storage_setup.sql`

#### Get Connection Details

1. Go to **Project Settings** → **API**
2. Save the following values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: For frontend (not used in no-auth setup)
   - **service_role key**: For backend (keep secret!)

3. Go to **Project Settings** → **Database**
4. Save the connection string if needed for direct PostgreSQL access

### 2. Upstash Redis Setup

#### Create Redis Database

1. Go to https://console.upstash.com
2. Click "Create Database"
3. Configure:
   - Name: `clipbrain-queue`
   - Type: Regional
   - Region: Choose closest to your backend deployment
   - TLS: Enabled (recommended)
4. Click "Create"

#### Get Connection URL

1. In your Redis database dashboard, go to **Details**
2. Copy the **Redis URL** (format: `redis://default:xxxxx@xxxxx.upstash.io:6379`)
3. Save this for your backend environment variables

### 3. Verify Setup

#### Check Database Tables

Run this query in Supabase SQL Editor to verify all tables were created:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

Expected tables:
- `collection_items`
- `collections`
- `notes`
- `transcript_chunks`
- `transcripts`
- `videos`

#### Check Indexes

Verify indexes were created:

```sql
SELECT 
  tablename, 
  indexname, 
  indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
```

#### Check Extensions

Verify extensions are enabled:

```sql
SELECT * FROM pg_extension WHERE extname IN ('vector', 'pg_trgm');
```

#### Check Storage Bucket

1. Go to **Storage** in Supabase dashboard
2. Verify `videos` bucket exists
3. Check that policies are set (should show service_role policies)

### 4. Environment Variables

Create a `.env` file in your backend directory with:

```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Upstash Redis
REDIS_URL=redis://default:xxxxx@xxxxx.upstash.io:6379

# AI Services (to be configured later)
DEEPGRAM_API_KEY=your_deepgram_key
GEMINI_API_KEY=your_gemini_key

# App Configuration
ALLOWED_PLATFORMS=youtube,instagram,tiktok,facebook
MAX_VIDEO_DURATION_SECONDS=7200
SIGNED_URL_TTL_SECONDS=900
```

## Database Schema Overview

### Tables

- **videos**: Main video metadata and processing status
- **transcripts**: Full transcript text for each video
- **transcript_chunks**: Time-segmented chunks with embeddings for search
- **notes**: AI-generated structured notes (summary, keywords, insights, etc.)
- **collections**: User-created collections for organizing videos
- **collection_items**: Junction table linking videos to collections

### Key Indexes

- **IVFFLAT index** on `transcript_chunks.embedding` for fast vector similarity search
- **GIN index** on `transcripts.full_text` for full-text search
- **GIN trigram index** on `videos.title` for fuzzy title matching
- **GIN index** on `notes.keywords` for tag filtering
- Standard B-tree indexes on foreign keys and frequently queried columns

## Maintenance

### Backup

Supabase automatically backs up your database daily. To create manual backups:

1. Go to **Database** → **Backups** in Supabase dashboard
2. Click "Create backup"

### Monitoring

Monitor your usage in Supabase dashboard:
- **Database** → **Database** for size and connection stats
- **Storage** → **Usage** for storage consumption
- **Reports** for API usage

### Index Tuning

If search performance degrades with large datasets, consider tuning the IVFFLAT index:

```sql
-- Rebuild with more lists for larger datasets
DROP INDEX idx_chunks_embedding;
CREATE INDEX idx_chunks_embedding ON transcript_chunks 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 200);  -- Increase from 100 to 200 for 10k+ chunks
```

## Troubleshooting

### pgvector Extension Not Found

If you get "extension vector does not exist":
1. Ensure you're on a Supabase project (pgvector is pre-installed)
2. Run `CREATE EXTENSION vector;` in SQL Editor
3. Check **Database** → **Extensions** to verify

### Storage Policies Not Working

If uploads fail with permission errors:
1. Verify bucket exists: Check **Storage** dashboard
2. Verify policies: Run `SELECT * FROM storage.policies WHERE bucket_id = 'videos';`
3. Ensure you're using the service_role key, not anon key

### Connection Issues

If backend can't connect to Supabase:
1. Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct
2. Check project is not paused (free tier pauses after inactivity)
3. Verify network/firewall allows outbound HTTPS

If backend can't connect to Redis:
1. Verify `REDIS_URL` format is correct
2. Check Upstash dashboard shows database is active
3. Verify TLS is enabled if using `rediss://` protocol

## Next Steps

After completing database setup:
1. Proceed to Task 2: Initialize backend FastAPI project structure
2. Configure environment variables in your backend
3. Test database connection from backend code
