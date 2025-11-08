# Design Document

## Overview

ClipBrain is architected as a personal PWA with a decoupled frontend and backend, leveraging free-tier cloud services for storage, compute, and AI processing. The system follows an asynchronous job-based architecture where video ingestion triggers a multi-stage pipeline: download → store → transcribe → generate notes → create embeddings. Search combines vector similarity and full-text matching for hybrid ranking. The design prioritizes reliability, cost efficiency, and simplicity while avoiding authentication complexity.

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Device                                 │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  PWA (Next.js + Tailwind)                                   │    │
│  │  - Share Target API                                         │    │
│  │  - Search Interface                                         │    │
│  │  - Video Player                                             │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Fly.io/Railway)                  │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │   API Routes     │         │   Worker Pool    │                 │
│  │  - /ingest       │◄────────┤   (RQ/Celery)    │                 │
│  │  - /search       │         │                  │                 │
│  │  - /job/{id}     │         └──────────────────┘                 │
│  │  - /item/{id}    │                 │                            │
│  │  - /export       │                 │                            │
│  └──────────────────┘                 │                            │
└────────────────────────────────────────┼────────────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
         ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
         │ Upstash Redis    │  │ Supabase         │  │ AI Services      │
         │ (Job Queue)      │  │ - PostgreSQL     │  │ - Deepgram       │
         │                  │  │ - pgvector       │  │ - Gemini API     │
         │                  │  │ - Storage        │  │                  │
         └──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Technology Stack

**Frontend (PWA)**
- Framework: Next.js 14+ (App Router)
- Styling: Tailwind CSS
- Hosting: Vercel Free
- Features: Web App Manifest, Share Target API, Service Worker (optional offline shell)

**Backend (API + Worker)**
- Framework: FastAPI (Python 3.11+, async)
- Job Queue: RQ (Redis Queue) with Upstash Redis Free
- Hosting: Fly.io Free or Railway Free
- Container: Docker with ffmpeg and yt-dlp pre-installed

**Database & Storage**
- Database: Supabase PostgreSQL with pgvector extension
- Object Storage: Supabase Storage (videos bucket)
- Hosting: Supabase Free tier

**AI Services**
- Transcription: Deepgram Enhanced Batch API (free tier)
- Notes Generation: Google Gemini API (text generation)
- Embeddings: Google Gemini Embeddings API

**Media Tools**
- Download: yt-dlp (latest stable)
- Processing: ffmpeg, ffprobe

### Data Flow

**Ingestion Pipeline:**
```
User shares URL → PWA → POST /ingest → FastAPI creates job → Redis Queue
                                                                    │
                                                                    ▼
                                                            Worker picks job
                                                                    │
                                    ┌───────────────────────────────┤
                                    │                               │
                                    ▼                               ▼
                            1. Download (yt-dlp)          2. Upload to Storage
                                    │                               │
                                    └───────────────┬───────────────┘
                                                    │
                                    ┌───────────────┴───────────────┐
                                    │                               │
                                    ▼                               ▼
                            3. Transcribe (Deepgram)    4. Generate Notes (Gemini)
                                    │                               │
                                    └───────────────┬───────────────┘
                                                    │
                                                    ▼
                                        5. Chunk & Embed (Gemini)
                                                    │
                                                    ▼
                                        6. Generate Previews (ffmpeg)
                                                    │
                                                    ▼
                                            Update status: done
```

**Search Flow:**
```
User query → PWA → POST /search → FastAPI
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                        ▼                           ▼
            Compute query embedding         Full-text search
            (Gemini Embeddings)             (PostgreSQL tsvector)
                        │                           │
                        ▼                           ▼
            Vector KNN search                Keyword/phrase match
            (pgvector cosine)                (GIN index + trigram)
                        │                           │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                            Hybrid ranking merge
                            (0.6 semantic + 0.4 keyword)
                                      │
                                      ▼
                            Group by video, top spans
                                      │
                                      ▼
                            Return results with metadata
```

## Components and Interfaces

### Frontend Components

**1. PWA Shell**
- Manifest configuration with Share Target API
- Service worker for offline UI (optional)
- Routes: `/`, `/search`, `/item/{id}`, `/share`, `/collections`, `/export`

**2. Core Pages**
- `HomePage`: Search bar, recent videos, tag chips, collection filters
- `SearchResultsPage`: Grouped result cards with snippets, deep links, preview buttons
- `ItemPage`: Video details, summary, tags, chapters, insights, transcript, preview player
- `SharePage`: Receives shared URL, calls `/ingest`, redirects to processing view
- `ProcessingView`: Live status updates via polling, stage indicators, failure messages

**3. UI Components**
- `SearchBar`: Supports tags, keywords, quoted phrases, natural language
- `ResultCard`: Title, platform chip, snippet, timestamp, "Open in app" + "Preview" buttons
- `VideoPlayer`: Inline preview playback with signed URLs
- `ChapterTOC`: Clickable chapter list with timestamps (for long videos)
- `TagChips`: Editable tag display and filtering
- `StatusIndicator`: Visual progress for queued → processing → done/failed

### Backend Components

**1. API Layer (FastAPI)**

```python
# Core endpoints
POST   /ingest          # Accept URL, create job, return job_id + video_id
GET    /job/{job_id}    # Poll job status
GET    /item/{video_id} # Retrieve video details, notes, transcript
POST   /search          # Hybrid search with query + optional filters
GET    /jump            # Generate deep link + signed play URL
GET    /export          # Stream ZIP with JSON + media files
GET    /healthz         # Health check
```

**2. Worker Layer (RQ/Celery)**

```python
# Job processor
@job('default', timeout='30m')
def process_video(video_id: str, source_url: str):
    # Execute pipeline stages
    pass

# Pipeline stages
def download_media(video_id, url) -> Path
def upload_to_storage(video_id, file_path) -> str
def transcribe_audio(video_id, storage_url) -> dict
def generate_notes(video_id, transcript) -> dict
def chunk_transcript(video_id, transcript_data) -> list
def generate_embeddings(chunks) -> list
def create_preview_clips(video_id, chunks) -> None
```

**3. Service Layer**

```python
# Downloader service
class MediaDownloader:
    def download(url: str) -> DownloadResult
    def canonicalize_url(url: str) -> str
    def detect_platform(url: str) -> Platform
    def is_restricted(error: Exception) -> bool

# Storage service
class StorageService:
    def upload_media(video_id: str, file: Path) -> str
    def generate_signed_url(path: str, ttl: int) -> str
    def upload_preview(video_id: str, clip: Path, start_ms: int, end_ms: int) -> str

# Transcription service
class TranscriptionService:
    def transcribe(audio_url: str) -> TranscriptResult
    def extract_word_timestamps(result: dict) -> list

# AI service
class AIService:
    def generate_notes(transcript: str, duration: int) -> NotesResult
    def generate_embedding(text: str) -> list[float]
    def batch_embeddings(texts: list[str]) -> list[list[float]]

# Search service
class SearchService:
    def hybrid_search(query: str, filters: dict) -> list[SearchResult]
    def vector_search(embedding: list[float], top_k: int) -> list
    def fulltext_search(query: str) -> list
    def merge_results(vector_results, text_results) -> list
```

### External Service Interfaces

**1. yt-dlp Integration**
```bash
# Command template
yt-dlp \
  -f "bestaudio[ext=m4a]/bestaudio/best" \
  --no-playlist \
  --no-warnings \
  --retries 2 \
  --socket-timeout 30 \
  -o "%(id)s.%(ext)s" \
  {URL}
```

**2. Deepgram API**
```python
# Request format
{
  "url": "https://signed-storage-url.com/audio.m4a",
  "model": "nova-2",
  "smart_format": true,
  "punctuate": true,
  "utterances": true,
  "diarize": false
}
```

**3. Gemini API**
```python
# Notes generation prompt
system_prompt = """
Extract structured information from this video transcript.
Return ONLY valid JSON with this exact schema:
{
  "summary": "string (8-10 lines max)",
  "keywords": ["string"] (12 max),
  "insights": ["string"],
  "steps": ["string"],
  "quotes": [{"text": "string", "start_ms": number}],
  "entities": {"people": [], "tools": [], "urls": []},
  "chapters": [{"title": "string", "start_ms": number}] (only if duration >= 300s)
}
"""

# Embedding request
model = "models/text-embedding-004"
content = chunk_text
```

## Data Models

### Database Schema

**videos**
```sql
CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url TEXT NOT NULL,
  canonical_url_hash TEXT UNIQUE NOT NULL,
  storage_path TEXT,
  platform TEXT NOT NULL CHECK (platform IN ('youtube', 'instagram', 'tiktok', 'facebook')),
  title TEXT,
  duration_seconds INTEGER,
  language TEXT,
  status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'done', 'failed')),
  fail_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created ON videos(created_at DESC);
CREATE INDEX idx_videos_canonical ON videos(canonical_url_hash);
```

**transcripts**
```sql
CREATE TABLE transcripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  full_text TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_transcripts_video ON transcripts(video_id);
CREATE INDEX idx_transcripts_fulltext ON transcripts USING GIN(to_tsvector('simple', full_text));
```

**transcript_chunks**
```sql
CREATE TABLE transcript_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  start_ms INTEGER NOT NULL,
  end_ms INTEGER NOT NULL,
  text TEXT NOT NULL,
  text_hash TEXT NOT NULL,
  embedding VECTOR(768), -- Adjust dimension for chosen Gemini model
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_chunks_video ON transcript_chunks(video_id, start_ms);
CREATE INDEX idx_chunks_embedding ON transcript_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_chunks_text_hash ON transcript_chunks(text_hash);
```

**notes**
```sql
CREATE TABLE notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  summary TEXT,
  keywords TEXT[] DEFAULT '{}',
  chapters JSONB DEFAULT '[]',
  insights JSONB DEFAULT '[]',
  steps JSONB DEFAULT '[]',
  quotes JSONB DEFAULT '[]',
  entities JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_notes_video ON notes(video_id);
CREATE INDEX idx_notes_keywords ON notes USING GIN(keywords);
```

**collections**
```sql
CREATE TABLE collections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE collection_items (
  collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (collection_id, video_id)
);

CREATE INDEX idx_collection_items_video ON collection_items(video_id);
```

### API Data Contracts

**POST /ingest Request**
```typescript
{
  url: string; // Required, must be from supported platform
}
```

**POST /ingest Response**
```typescript
{
  job_id: string;
  video_id: string;
}
```

**GET /job/{job_id} Response**
```typescript
{
  status: 'queued' | 'processing' | 'done' | 'failed';
  video_id: string;
  fail_reason?: string;
  current_stage?: 'download' | 'upload' | 'transcribe' | 'notes' | 'embeddings' | 'previews';
}
```

**GET /item/{video_id} Response**
```typescript
{
  video: {
    id: string;
    title: string;
    platform: string;
    duration_seconds: number;
    source_url: string;
    storage_url: string; // Signed URL
    created_at: string;
  };
  notes: {
    summary: string;
    keywords: string[];
    chapters: Array<{ title: string; start_ms: number }>;
    insights: string[];
    steps: string[];
    quotes: Array<{ text: string; start_ms: number }>;
    entities: { people: string[]; tools: string[]; urls: string[] };
  };
  transcript_preview: Array<{
    start_ms: number;
    end_ms: number;
    text: string;
  }>;
  status: string;
}
```

**POST /search Request**
```typescript
{
  q: string; // Query text
  top_k?: number; // Default 20
  tags?: string[]; // Filter by tags
  platform?: string; // Filter by platform
}
```

**POST /search Response**
```typescript
{
  results: Array<{
    video_id: string;
    title: string;
    platform: string;
    start_ms: number;
    end_ms: number;
    snippet: string;
    score: number;
    tags: string[];
    chapter_title?: string;
    source_url: string;
    deep_link?: string; // YouTube only
    preview_url: string; // Signed URL for inline playback
  }>;
  total: number;
  query_time_ms: number;
}
```

**GET /jump Response**
```typescript
{
  deep_link: string; // Original platform URL with timestamp (if supported)
  signed_play_url: string; // Supabase signed URL
  start_seconds: number;
}
```

## Error Handling

### Error Codes and User Messages

**Download Errors**
- `RESTRICTED_CONTENT_UNSUPPORTED`: "This video appears private or restricted. Public links only."
- `NOT_FOUND_OR_REMOVED`: "The source link may be removed or region-blocked."
- `PLATFORM_BLOCKED_TEMPORARILY`: "The platform is temporarily blocking downloads; try later."
- `UNSUPPORTED_PLATFORM`: "This platform is not supported. Try YouTube, Instagram, TikTok, or Facebook."

**Processing Errors**
- `TRANSCRIPTION_FAILED`: "Audio transcription failed. The audio may be corrupted or unsupported."
- `NOTES_PARTIAL`: "Notes generated with incomplete data. Transcript is still searchable."
- `EMBEDDING_PARTIAL`: "Semantic search unavailable for this video. Keyword search still works."
- `STORAGE_UPLOAD_FAILED`: "Failed to store media. Please try again."

### Retry Strategy

**Download Stage**
- Retry: 1 attempt with 5-second delay
- Timeout: 30 seconds per attempt
- Failure action: Mark failed with appropriate error code

**Transcription Stage**
- Retry: 1 attempt with 10-second delay
- Timeout: 5 minutes for batch processing
- Failure action: Mark TRANSCRIPTION_FAILED, stop pipeline

**Notes Generation Stage**
- Retry: 1 attempt with JSON schema clarifier
- Timeout: 60 seconds per attempt
- Failure action: Store raw text as notes_raw_text, mark NOTES_PARTIAL, continue pipeline

**Embeddings Stage**
- Retry: 1 attempt per batch with 5-second delay
- Timeout: 30 seconds per batch
- Failure action: Mark EMBEDDING_PARTIAL, continue (keyword search still functional)

**Storage Upload Stage**
- Retry: 1 attempt with 10-second delay
- Timeout: 2 minutes per file
- Failure action: Mark STORAGE_UPLOAD_FAILED, stop pipeline

### Idempotency

- All jobs are idempotent by `canonical_url_hash`
- Before creating a new job, check if `canonical_url_hash` exists
- If exists and status is `done`: return existing video_id
- If exists and status is `failed`: allow retry by creating new job
- If exists and status is `queued` or `processing`: return existing job_id

## Testing Strategy

### Unit Tests

**Backend Services**
- `MediaDownloader`: Test URL canonicalization, platform detection, error classification
- `StorageService`: Test signed URL generation, path construction
- `AIService`: Test prompt formatting, JSON validation, embedding batching
- `SearchService`: Test score normalization, result merging, grouping logic

**Frontend Components**
- `SearchBar`: Test query parsing (tags, quotes, keywords)
- `ResultCard`: Test deep link generation, preview button behavior
- `StatusIndicator`: Test status transitions and error display

### Integration Tests

**Ingestion Pipeline**
- Test full pipeline with mock YouTube URL (public, short video)
- Verify database state at each stage
- Test failure scenarios (restricted content, transcription error)
- Verify idempotency with duplicate URLs

**Search Flow**
- Test vector search with known embeddings
- Test full-text search with exact phrases
- Test hybrid ranking with mixed results
- Verify result grouping and span selection

**API Endpoints**
- Test `/ingest` with valid and invalid URLs
- Test `/job/{id}` polling behavior
- Test `/search` with various query types
- Test `/export` ZIP generation

### End-to-End Tests

**Happy Path**
1. Share public YouTube video URL
2. Poll until status = done
3. Verify transcript, notes, chunks, embeddings exist
4. Search for content from video
5. Verify result includes correct timestamp
6. Click deep link and verify YouTube URL format
7. Play inline preview

**Error Scenarios**
1. Share private video → verify RESTRICTED_CONTENT_UNSUPPORTED
2. Share invalid URL → verify rejection before queue
3. Simulate transcription failure → verify TRANSCRIPTION_FAILED
4. Simulate Gemini timeout → verify NOTES_PARTIAL with fallback

### Performance Tests

**Search Latency**
- Target: <1.5s for typical queries
- Test with 100, 500, 1000 videos in database
- Measure vector search, full-text search, and merge time separately

**Ingestion Throughput**
- Test concurrent job processing (3-5 simultaneous)
- Verify queue doesn't block on long videos
- Measure average time per stage

**Storage Efficiency**
- Verify audio-only downloads are smaller than video
- Test deduplication prevents re-download
- Measure embedding cache hit rate

### Manual Testing Checklist

- [ ] Install PWA on mobile device
- [ ] Share YouTube video from YouTube app
- [ ] Share Instagram Reel from Instagram app
- [ ] Share TikTok from TikTok app
- [ ] Verify processing status updates in real-time
- [ ] Search with natural language question
- [ ] Search with exact phrase in quotes
- [ ] Search with tag filter
- [ ] Click "Open in app" for YouTube result → verify timestamp
- [ ] Play inline preview for Instagram result
- [ ] Create collection and add videos
- [ ] Edit tags on a video
- [ ] Export data and verify ZIP contents
- [ ] Test offline UI shell (if implemented)

## Security Considerations

### No-Auth Security Model

**Access Control**
- Deploy on unlisted subdomain (e.g., `clipbrain-xyz123.fly.dev`)
- Optional: Configure IP allow-list at reverse proxy for `/ingest` and `/export`
- No user accounts, sessions, or cookies

**API Key Management**
- All API keys stored in server environment variables only
- Frontend never receives or stores API keys
- Supabase service role key used server-side only

**Signed URLs**
- Generate short-lived signed URLs (5-15 minute TTL) for media access
- Frontend requests signed URLs from backend on-demand
- No direct frontend-to-Supabase communication

**Input Validation**
- Validate URL format and platform before queuing
- Sanitize all user inputs (search queries, collection names)
- Reject URLs with suspicious patterns (localhost, internal IPs)

**Rate Limiting**
- Implement basic rate limiting on `/ingest` (e.g., 10 requests/hour per IP)
- Implement rate limiting on `/search` (e.g., 100 requests/hour per IP)
- Use Redis for distributed rate limit tracking

### Data Privacy

**Content Scope**
- Only public or unlisted content (no private/restricted)
- No cookies or session handling to bypass platform protections
- Clear error messages when content is restricted

**Storage**
- All data stored in Supabase (single-region deployment)
- No third-party analytics or tracking
- Export functionality for complete data portability

## Deployment Architecture

### Frontend Deployment (Vercel)

```yaml
# vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://clipbrain-api.fly.dev"
  }
}
```

### Backend Deployment (Fly.io)

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN pip install yt-dlp

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```toml
# fly.toml
app = "clipbrain-api"

[build]
  dockerfile = "Dockerfile"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[env]
  REDIS_URL = "redis://upstash-url"
  SUPABASE_URL = "https://xxx.supabase.co"
```

### Environment Variables

**Backend (.env)**
```bash
# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# Queue
REDIS_URL=redis://upstash-url

# AI Services
DEEPGRAM_API_KEY=xxx
GEMINI_API_KEY=xxx

# App Config
ALLOWED_PLATFORMS=youtube,instagram,tiktok,facebook
MAX_VIDEO_DURATION_SECONDS=7200
SIGNED_URL_TTL_SECONDS=900
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=https://clipbrain-api.fly.dev
```

### Monitoring and Logging

**Structured Logging**
```python
import structlog

logger = structlog.get_logger()

# Log format
logger.info(
    "pipeline_stage_complete",
    job_id=job_id,
    video_id=video_id,
    stage="transcribe",
    duration_ms=elapsed,
    status="success"
)
```

**Health Check Endpoint**
```python
@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "redis": await check_redis(),
        "supabase": await check_supabase(),
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Metrics to Track**
- Jobs processed per hour
- Average pipeline duration per stage
- Failure rate by error code
- Search query latency (p50, p95, p99)
- Storage usage growth rate
- API quota usage (Deepgram, Gemini)

## Cost Optimization

### Free Tier Limits

**Vercel Free**
- 100 GB bandwidth/month
- Unlimited deployments
- Automatic HTTPS

**Fly.io Free**
- 3 shared-cpu-1x VMs
- 160 GB bandwidth/month
- 3 GB persistent storage

**Upstash Redis Free**
- 10,000 commands/day
- 256 MB storage

**Supabase Free**
- 500 MB database
- 1 GB file storage
- 2 GB bandwidth/month
- 50,000 monthly active users (not applicable)

**Deepgram Free**
- $200 credit (≈45 hours of audio)

**Gemini Free**
- 60 requests/minute
- 1,500 requests/day

### Optimization Strategies

**Download Optimization**
- Prefer audio-only formats (10x smaller than video)
- Use lowest bitrate that preserves speech clarity
- Skip download if canonical URL already processed

**Transcription Optimization**
- Use batch API (cheaper than streaming)
- Cap maximum duration at 2 hours per video
- Cache transcripts indefinitely

**Embedding Optimization**
- Cache embeddings by text_hash
- Batch embedding requests (up to 100 texts)
- Only re-embed if chunk text changes

**Storage Optimization**
- Store audio-only when possible
- Generate preview clips on-demand (optional)
- Compress preview clips with H.264 + AAC

**Search Optimization**
- Use IVFFLAT index for vector search (faster than exact)
- Limit vector search to top 50 candidates before merge
- Cache popular query embeddings (optional)

## Future Enhancements (Out of Scope for V1)

- Multi-user support with authentication
- Real-time collaborative collections
- Browser extension for one-click capture
- Automatic playlist/channel monitoring
- Advanced analytics (watch time, popular topics)
- Custom AI models for domain-specific content
- Mobile native apps (iOS/Android)
- Webhook integrations (Zapier, IFTTT)
- Advanced chapter detection with scene analysis
- Automatic highlight reel generation
