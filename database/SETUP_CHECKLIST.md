# Database Setup Checklist

Use this checklist to ensure all infrastructure components are properly configured.

## ☐ Supabase Setup

### Create Project
- [ ] Sign up at https://supabase.com (if not already registered)
- [ ] Create new project named "clipbrain"
- [ ] Save database password securely
- [ ] Wait for project provisioning to complete (~2-3 minutes)

### Enable Extensions
- [ ] Navigate to Database → Extensions
- [ ] Enable `vector` extension
- [ ] Enable `pg_trgm` extension (should be enabled by default)
- [ ] Verify both extensions show as "Enabled"

### Run Migrations
- [ ] Open SQL Editor in Supabase dashboard
- [ ] Create new query
- [ ] Copy contents of `migrations/001_initial_schema.sql`
- [ ] Execute query (should complete without errors)
- [ ] Create another new query
- [ ] Copy contents of `migrations/002_storage_setup.sql`
- [ ] Execute query (should complete without errors)

### Verify Tables
- [ ] Run verification query in SQL Editor:
  ```sql
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema = 'public' ORDER BY table_name;
  ```
- [ ] Confirm all 6 tables exist:
  - [ ] collection_items
  - [ ] collections
  - [ ] notes
  - [ ] transcript_chunks
  - [ ] transcripts
  - [ ] videos

### Verify Storage Bucket
- [ ] Navigate to Storage in Supabase dashboard
- [ ] Confirm "videos" bucket exists
- [ ] Click on bucket and verify policies are set
- [ ] Should see 4 policies for service_role (INSERT, SELECT, UPDATE, DELETE)

### Save Credentials
- [ ] Navigate to Project Settings → API
- [ ] Copy and save **Project URL** (format: `https://xxxxx.supabase.co`)
- [ ] Copy and save **service_role key** (keep this secret!)
- [ ] Do NOT share service_role key in version control

## ☐ Upstash Redis Setup

### Create Database
- [ ] Sign up at https://upstash.com (if not already registered)
- [ ] Click "Create Database"
- [ ] Enter name: "clipbrain-queue"
- [ ] Select type: Regional
- [ ] Choose region closest to your backend deployment location
- [ ] Enable TLS (recommended)
- [ ] Click "Create"

### Save Credentials
- [ ] Navigate to database Details tab
- [ ] Copy **Redis URL** (format: `redis://default:xxxxx@xxxxx.upstash.io:6379`)
- [ ] Save this URL securely
- [ ] Do NOT share Redis URL in version control

## ☐ Environment Configuration

### Create .env File
- [ ] Create `.env` file in backend directory (or project root)
- [ ] Add the following variables:
  ```bash
  SUPABASE_URL=https://xxxxx.supabase.co
  SUPABASE_SERVICE_KEY=your_service_role_key_here
  REDIS_URL=redis://default:xxxxx@xxxxx.upstash.io:6379
  ```
- [ ] Add `.env` to `.gitignore` to prevent committing secrets

### Verify .gitignore
- [ ] Ensure `.gitignore` includes:
  ```
  .env
  .env.local
  .env.*.local
  ```

## ☐ Verification

### Install Verification Dependencies
- [ ] Install Python dependencies:
  ```bash
  pip install asyncpg redis python-dotenv
  ```

### Run Verification Script
- [ ] Execute verification script:
  ```bash
  python database/verify_setup.py
  ```
- [ ] Confirm all checks pass (green checkmarks)
- [ ] If any checks fail, review error messages and fix issues

### Manual Verification (Optional)
- [ ] Test Supabase connection from SQL Editor
- [ ] Test Redis connection from Upstash console (Data Browser)
- [ ] Verify you can insert a test row into `videos` table
- [ ] Verify you can query the test row back

## ☐ Documentation

### Update Project Documentation
- [ ] Document your Supabase project URL in team docs (if applicable)
- [ ] Document Redis instance region/name in team docs (if applicable)
- [ ] Do NOT document actual credentials in shared docs

### Save Backup Information
- [ ] Save Supabase project name and region
- [ ] Save Upstash database name and region
- [ ] Store credentials in secure password manager

## Troubleshooting

### Common Issues

**"Extension vector does not exist"**
- Solution: Enable pgvector in Database → Extensions

**"Permission denied for table storage.objects"**
- Solution: Verify you're using service_role key, not anon key
- Solution: Re-run `migrations/002_storage_setup.sql`

**"Connection refused" to PostgreSQL**
- Solution: Check Supabase project is not paused (free tier auto-pauses)
- Solution: Verify SUPABASE_URL format is correct
- Solution: Check firewall allows outbound HTTPS

**"Connection refused" to Redis**
- Solution: Verify REDIS_URL format is correct
- Solution: Check Upstash database is active in console
- Solution: Verify TLS setting matches URL protocol (redis:// vs rediss://)

**"Table already exists" error**
- Solution: Tables were already created, this is OK
- Solution: If you need to reset, drop tables manually first

## Next Steps

Once all checklist items are complete:

1. ✅ Mark Task 1 as complete in tasks.md
2. ➡️ Proceed to Task 2: Initialize backend FastAPI project structure
3. 🔑 Configure AI service API keys (Deepgram, Gemini) when ready

---

**Setup completed on:** _________________

**Verified by:** _________________
