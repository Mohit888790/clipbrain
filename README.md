# 🎬 ClipBrain - Personal Video Knowledge Base

Transform your video library into a searchable knowledge base with AI-powered transcription, notes, and semantic search.

## ✨ Features

- 🎥 **Multi-Platform Support** - YouTube, Instagram, TikTok, Facebook
- 🎤 **Auto Transcription** - Powered by Deepgram
- 🤖 **AI Notes** - Summaries, keywords, insights, quotes, chapters
- 🔍 **Hybrid Search** - Semantic + keyword search
- 📚 **Collections** - Organize your videos
- 🏷️ **Tags** - Categorize and filter
- 📦 **Export** - Download all your data
- 🔒 **Private** - Your data, your control

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free)
- Upstash Redis account (free)
- Deepgram API key
- Google Gemini API key

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/clipbrain.git
cd clipbrain

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Setup Database

1. Go to https://app.supabase.com/project/YOUR_PROJECT/sql
2. Run `database/migrations/001_initial_schema.sql`
3. Run `database/migrations/002_storage_setup.sql`

### 3. Run Locally

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Worker
cd backend
python workers/worker.py
```

### 4. Test It

```bash
curl http://localhost:8000/healthz
```

## 🚂 Deploy to Railway

### Quick Deploy (5 minutes)

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Railway**:
   - Go to https://railway.app/dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables
   - Deploy!

3. **Deploy Worker**:
   - Click "New Service" → Same repo
   - Set start command: `cd backend && python workers/worker.py`
   - Add same environment variables

**Detailed Guide**: See `RAILWAY_QUICK_DEPLOY.md`

## 📖 API Documentation

### Ingest Video
```bash
POST /ingest
Body: {"url": "VIDEO_URL"}
```

### Check Status
```bash
GET /job/{video_id}
```

### Search Videos
```bash
POST /search
Body: {"q": "search query", "top_k": 20}
```

### Get Video Details
```bash
GET /item/{video_id}
```

**Full API Docs**: http://localhost:8000/docs (when running)

## 📁 Project Structure

```
clipbrain/
├── backend/              # FastAPI backend
│   ├── main.py          # API entry point
│   ├── services/        # Business logic
│   ├── routes/          # API endpoints
│   ├── workers/         # Background jobs
│   └── middleware/      # Rate limiting, etc.
├── database/            # Database migrations
├── frontend/            # Next.js frontend (minimal)
└── docs/               # Documentation
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL + pgvector
- Redis (job queue)
- Docker

**AI Services:**
- Deepgram (transcription)
- Google Gemini (notes + embeddings)

**Infrastructure:**
- Supabase (database + storage)
- Upstash (Redis)
- Railway (hosting)
- Vercel (frontend)

**Media Tools:**
- yt-dlp (download)
- ffmpeg (processing)

## 📚 Documentation

- **Quick Start**: `QUICK_START.md`
- **Railway Deployment**: `RAILWAY_QUICK_DEPLOY.md`
- **Full Deployment Guide**: `DEPLOYMENT.md`
- **Alternative Platforms**: `DEPLOYMENT_ALTERNATIVES.md`
- **Database Setup**: `database/README.md`
- **Test Results**: `TEST_RESULTS.md`
- **Project Summary**: `PROJECT_COMPLETE.md`

## 🧪 Testing

```bash
# Run connection tests
python backend/test_connections.py

# Test API endpoints
curl http://localhost:8000/healthz
curl -X POST http://localhost:8000/ingest -d '{"url":"..."}'
```

## 💰 Cost

Everything runs on **free tiers**:

- Supabase: 500 MB database, 1 GB storage
- Upstash: 10k commands/day
- Railway: $5 credit/month (~500 hours)
- Deepgram: $200 credit (≈45 hours)
- Gemini: 60 req/min, 1500 req/day

**Total: $0/month** for personal use!

## 🎯 Roadmap

- [x] Backend API (100% complete)
- [x] Video ingestion pipeline
- [x] AI transcription & notes
- [x] Hybrid search
- [x] Collections & tags
- [x] Railway deployment
- [ ] Frontend UI components
- [ ] PWA with Share Target
- [ ] Mobile app
- [ ] Batch ingestion
- [ ] Playlist support

## 🤝 Contributing

This is a personal project, but feel free to fork and customize for your needs!

## 📄 License

MIT License - See LICENSE file

## 🆘 Support

- **Issues**: Check `TEST_RESULTS.md` for known issues
- **Deployment**: See `RAILWAY_QUICK_DEPLOY.md`
- **Database**: See `database/README.md`

## 🌟 Acknowledgments

Built with:
- FastAPI
- Supabase
- Deepgram
- Google Gemini
- Railway
- yt-dlp
- ffmpeg

---

**Ready to build your video knowledge base?** Start with `QUICK_START.md` or `RAILWAY_QUICK_DEPLOY.md`! 🚀
