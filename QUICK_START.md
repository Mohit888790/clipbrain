# ClipBrain - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- Supabase account (free)
- Upstash Redis account (free)
- Deepgram API key
- Google Gemini API key

### 1. Clone & Setup (1 minute)

```bash
cd clipbrain
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Configure Environment (1 minute)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

Required variables:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
REDIS_URL=rediss://default:token@your-redis.upstash.io:6379
DEEPGRAM_API_KEY=your_deepgram_key
GEMINI_API_KEY=your_gemini_key
```

### 3. Run Database Migrations (2 minutes)

1. Go to https://app.supabase.com/project/YOUR_PROJECT/sql
2. Run `database/migrations/001_initial_schema.sql`
3. Run `database/migrations/002_storage_setup.sql`

### 4. Start Services (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Worker:**
```bash
cd backend
python workers/worker.py
```

### 5. Test It! (30 seconds)

```bash
# Health check
curl http://localhost:8000/healthz

# Ingest a video
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Check status (use the video_id from above)
curl http://localhost:8000/job/VIDEO_ID

# Get video details
curl http://localhost:8000/item/VIDEO_ID
```

## 📖 API Quick Reference

### Ingest Video
```bash
POST /ingest
Body: {"url": "VIDEO_URL"}
Response: {"job_id": "...", "video_id": "..."}
```

### Check Status
```bash
GET /job/{video_id}
Response: {"status": "processing|done|failed", "current_stage": "..."}
```

### Get Video
```bash
GET /item/{video_id}
Response: {video, notes, transcript_preview}
```

### Search
```bash
POST /search
Body: {"q": "search query", "top_k": 20}
Response: {results: [...], total: N}
```

### Collections
```bash
POST /collections
Body: {"name": "My Collection"}

GET /collections
Response: [{id, name, video_count}, ...]
```

### Export
```bash
GET /export
Response: ZIP file with all data
```

## 🐛 Troubleshooting

### "Address already in use"
```bash
# Kill existing process
pkill -f "python.*main.py"
# Or use different port
uvicorn main:app --port 8001
```

### "Module not found"
```bash
# Activate venv
source venv/bin/activate
# Reinstall dependencies
pip install -r backend/requirements.txt
```

### "Database connection failed"
- Check SUPABASE_URL and SUPABASE_SERVICE_KEY
- Verify migrations were run
- Check Supabase project is active

### "Redis connection failed"
- Check REDIS_URL format: `rediss://default:TOKEN@host:6379`
- Verify Upstash database is active
- Check TLS is enabled (rediss://)

## 📚 Documentation

- **Full Guide**: `PROJECT_COMPLETE.md`
- **Deployment**: `DEPLOYMENT.md`
- **Test Results**: `TEST_RESULTS.md`
- **Database Setup**: `database/README.md`
- **API Docs**: http://localhost:8000/docs (when running)

## 🎯 Next Steps

1. **Test all platforms**: YouTube, Instagram, TikTok, Facebook
2. **Try search**: Search your ingested videos
3. **Create collections**: Organize your videos
4. **Export data**: Download your library
5. **Deploy**: Follow `DEPLOYMENT.md` to deploy to Fly.io

## 💡 Tips

- Use short videos for testing (30-60 seconds)
- Check worker logs if processing fails
- Monitor Deepgram and Gemini API quotas
- Use `/healthz` to verify all services are connected
- Check `/docs` for interactive API documentation

## 🆘 Need Help?

1. Check `TEST_RESULTS.md` for known issues
2. Review `DEPLOYMENT.md` for deployment help
3. See `database/README.md` for database issues
4. Check logs in `/tmp/clipbrain.log` and `/tmp/clipbrain_worker.log`

---

**Ready to build your video knowledge base!** 🎉
