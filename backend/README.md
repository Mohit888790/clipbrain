# ClipBrain Backend

FastAPI backend for video ingestion and search.

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── database.py            # PostgreSQL connection pool (asyncpg)
├── supabase_client.py     # Supabase REST API client
├── storage.py             # Supabase Storage service
├── models.py              # Pydantic models for API
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container definition
├── services/             # Business logic services
├── routes/               # API route handlers
├── workers/              # Background job workers
└── test_connections.py   # Connection verification script
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root (not in backend/) with:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
REDIS_URL=rediss://default:token@your-redis.upstash.io:6379
DEEPGRAM_API_KEY=your_deepgram_key
GEMINI_API_KEY=your_gemini_key
```

### 3. Verify Connections

```bash
python backend/test_connections.py
```

All checks should pass before proceeding.

## Running the Backend

### Development Mode

```bash
python backend/main.py
```

Or with uvicorn directly:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode (Docker)

```bash
docker build -t clipbrain-backend backend/
docker run -p 8000:8000 --env-file .env clipbrain-backend
```

## API Endpoints

### Health Check

```bash
GET /healthz
```

Returns health status of Redis and Supabase connections.

### Root

```bash
GET /
```

Returns API information.

## Testing

### Test All Connections

```bash
python backend/test_connections.py
```

This verifies:
- ✅ Redis connection (Upstash)
- ✅ Database connection (Supabase REST API)
- ✅ Storage bucket exists (Supabase Storage)
- ✅ Deepgram API key is valid
- ✅ Gemini API key is valid

### Test Health Endpoint

```bash
curl http://localhost:8000/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "redis": true,
  "supabase": true,
  "timestamp": "2025-01-08T12:00:00.000Z"
}
```

## Configuration

All configuration is managed through environment variables using `pydantic-settings`.

See `config.py` for available settings:

- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Service role key (keep secret!)
- `REDIS_URL` - Upstash Redis connection URL
- `DEEPGRAM_API_KEY` - Deepgram API key for transcription
- `GEMINI_API_KEY` - Google Gemini API key for AI
- `ALLOWED_PLATFORMS` - Comma-separated list of supported platforms
- `MAX_VIDEO_DURATION_SECONDS` - Maximum video duration (default: 7200)
- `SIGNED_URL_TTL_SECONDS` - Signed URL expiration (default: 900)
- `INGEST_RATE_LIMIT_PER_HOUR` - Rate limit for ingestion (default: 10)
- `SEARCH_RATE_LIMIT_PER_HOUR` - Rate limit for search (default: 100)

## Database Access

The backend uses two methods for database access:

1. **Supabase REST API** (`supabase_client.py`) - For CRUD operations
   - Works from anywhere (no direct PostgreSQL access needed)
   - Recommended for most operations

2. **Direct PostgreSQL** (`database.py`) - For complex queries
   - Requires network access to Supabase PostgreSQL
   - Used for advanced queries with joins, aggregations, etc.

## Storage Service

The `storage.py` module provides methods for:

- `upload_media()` - Upload video/audio files
- `generate_signed_url()` - Create temporary access URLs
- `upload_preview()` - Upload preview clips
- `delete_file()` - Remove files from storage

All files are stored in the `videos` bucket with paths like:
- `{video_id}/original.m4a` - Original media file
- `{video_id}/previews/{start_ms}_{end_ms}.mp4` - Preview clips

## Next Steps

After Task 2 is complete, proceed to:

**Task 3**: Implement media downloader service
- URL canonicalization
- Platform detection
- yt-dlp wrapper
- Error classification

## Troubleshooting

### "Network is unreachable" for PostgreSQL

This is expected if you don't have direct PostgreSQL access. Use the Supabase REST API client instead (`supabase_client.py`).

### Redis connection fails

- Verify `REDIS_URL` starts with `rediss://` (with TLS)
- Check Upstash dashboard shows database is active
- Ensure URL includes the token: `rediss://default:TOKEN@host:6379`

### Storage upload fails

- Verify bucket `videos` exists in Supabase Storage
- Check you're using `service_role` key, not `anon` key
- Ensure storage policies were created (run migration 002)

### API keys invalid

- Deepgram: Check key at https://console.deepgram.com
- Gemini: Check key at https://aistudio.google.com/apikey
- Ensure no extra spaces or quotes in `.env` file

## Development Notes

- The backend uses async/await throughout for better performance
- All database operations should use connection pooling
- Rate limiting will be implemented in Task 14
- Worker processes for background jobs will be added in Task 8

## License

Part of the ClipBrain project.
