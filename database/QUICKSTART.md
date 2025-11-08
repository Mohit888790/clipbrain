# Database Setup Quick Start

Get your ClipBrain database up and running in 10 minutes.

## Prerequisites

- [ ] Supabase account (sign up at https://supabase.com)
- [ ] Upstash account (sign up at https://upstash.com)

## Step 1: Create Supabase Project (3 minutes)

1. Go to https://app.supabase.com
2. Click **"New Project"**
3. Fill in:
   - **Name**: `clipbrain`
   - **Database Password**: Generate and save securely
   - **Region**: Choose closest to you
4. Click **"Create new project"**
5. Wait for provisioning (~2 minutes)

## Step 2: Run Database Migrations (2 minutes)

1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New query"**
3. Copy entire contents of `database/migrations/001_initial_schema.sql`
4. Paste and click **"Run"**
5. Wait for success message
6. Click **"New query"** again
7. Copy entire contents of `database/migrations/002_storage_setup.sql`
8. Paste and click **"Run"**
9. Wait for success message

## Step 3: Get Supabase Credentials (1 minute)

1. Go to **Project Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **service_role key**: `eyJhbG...` (long string)
3. Save them - you'll need them next

## Step 4: Create Upstash Redis (2 minutes)

1. Go to https://console.upstash.com
2. Click **"Create Database"**
3. Fill in:
   - **Name**: `clipbrain-queue`
   - **Type**: Regional
   - **Region**: Choose closest to your backend
   - **TLS**: Enabled
4. Click **"Create"**
5. Go to **Details** tab
6. Copy **Redis URL**: `redis://default:xxxxx@xxxxx.upstash.io:6379`

## Step 5: Configure Environment (1 minute)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```bash
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbG...
   REDIS_URL=redis://default:xxxxx@xxxxx.upstash.io:6379
   ```

3. Save the file

## Step 6: Verify Setup (1 minute)

1. Install verification dependencies:
   ```bash
   pip install asyncpg redis python-dotenv
   ```

2. Run verification script:
   ```bash
   python database/verify_setup.py
   ```

3. You should see all green checkmarks ✅

## Done! 🎉

Your database is ready. Next steps:

1. Mark Task 1 as complete in `tasks.md`
2. Proceed to Task 2: Initialize backend FastAPI project
3. Start building the ingestion pipeline

## Troubleshooting

### "Extension vector does not exist"

**Fix**: Enable pgvector extension
1. Go to **Database** → **Extensions** in Supabase
2. Search for "vector"
3. Click "Enable"

### "Connection refused"

**Fix**: Check your credentials
1. Verify `SUPABASE_URL` is correct (should start with `https://`)
2. Verify `SUPABASE_SERVICE_KEY` is the **service_role** key, not anon key
3. Verify `REDIS_URL` is correct (should start with `redis://`)

### "Permission denied for table storage.objects"

**Fix**: Re-run storage migration
1. Go to SQL Editor
2. Run `database/migrations/002_storage_setup.sql` again

### Still having issues?

Check the detailed guides:
- `database/README.md` - Full setup instructions
- `database/SETUP_CHECKLIST.md` - Step-by-step checklist
- `database/SCHEMA_DESIGN.md` - Schema documentation

## What Was Created?

### Database Tables (6)
- ✅ `videos` - Video metadata and status
- ✅ `transcripts` - Full transcript text
- ✅ `transcript_chunks` - Time-segmented chunks with embeddings
- ✅ `notes` - AI-generated structured notes
- ✅ `collections` - User collections
- ✅ `collection_items` - Video-to-collection mappings

### Indexes (13)
- ✅ IVFFLAT index for vector search
- ✅ GIN indexes for full-text search
- ✅ Trigram index for fuzzy title search
- ✅ B-tree indexes for foreign keys and common queries

### Storage
- ✅ `videos` bucket for media files
- ✅ Storage policies for service role access

### Extensions
- ✅ pgvector for vector similarity search
- ✅ pg_trgm for trigram fuzzy matching

## Cost Estimate

All services used are on **free tiers**:

- **Supabase Free**: 500 MB database, 1 GB storage
- **Upstash Free**: 10k commands/day, 256 MB storage
- **Total cost**: $0/month

You can store approximately:
- ~1000 videos (with transcripts and embeddings)
- ~50k transcript chunks
- ~1 GB of audio files

## Security Notes

⚠️ **Important**:
- Never commit `.env` file to git
- Keep `service_role` key secret
- Don't share Redis URL publicly
- Use IP allow-list for production (optional)

## Next Steps

Ready to build? Continue with:

→ **Task 2**: Initialize backend FastAPI project structure
→ **Task 3**: Implement media downloader service
→ **Task 4**: Implement storage service

Happy coding! 🚀
