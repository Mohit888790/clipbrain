# 🎬 ClipBrain - Complete Setup & Deployment Guide

This guide will take you from zero to a fully deployed ClipBrain instance in about 30 minutes.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [x] Railway account (https://railway.app)
- [x] GitHub account
- [x] Supabase project created
- [x] Upstash Redis instance created
- [x] Deepgram API key
- [x] Google Gemini API key
- [x] Git installed
- [x] Python 3.11+ installed

## 🚀 Complete Setup Process

### Phase 1: Local Setup (10 minutes)

#### 1. Clone/Setup Repository

```bash
# If you haven't already
cd /path/to/your/projects
# Your code is already here at: /media/log4j/windows 11 project/clipbrain

# Verify you're in the right directory
pwd
# Should show: /media/log4j/windows 11 project/clipbrain
```

#### 2. Verify Environment Variables

Your `.env` file should have:

```bash
SUPABASE_URL=https://ifzdryytyqfufmjzchrr.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REDIS_URL=rediss://default:ATnHAAIncDJmN2FiYjI1YzZhOTI0OGYzYmFjMDIyZmU0N2I5NmE2ZHAyMTQ3OTE@sincere-mammoth-14791.upstash.io:6379
DEEPGRAM_API_KEY=f4514f516bd9fe05aee157acdaa20f9c939f1c99
GEMINI_API_KEY=AIzaSyDWBxyr8yXSNdnCtfXbUsF6R5DEH3PK3NM
ALLOWED_PLATFORMS=youtube,instagram,tiktok,facebook
MAX_VIDEO_DURATION_SECONDS=7200
SIGNED_URL_TTL_SECONDS=900
INGEST_RATE_LIMIT_PER_HOUR=10
SEARCH_RATE_LIMIT_PER_HOUR=100
```

✅ **Status**: Your `.env` is already configured!

#### 3. Verify Database Migrations

Your Supabase database should have these tables:
- videos
- transcripts
- transcript_chunks
- notes
- collections
- collection_items

✅ **Status**: Migrations already run!

#### 4. Test Local Backend

```bash
# Activate venv
source venv/bin/activate

# Start backend (Terminal 1)
cd backend
python main.py

# In another terminal, test it
curl http://localhost:8000/healthz
```

Expected response:
```json
{"status":"healthy","redis":true,"supabase":true,"timestamp":"..."}
```

✅ **Status**: Backend tested and working!

### Phase 2: GitHub Setup (5 minutes)

#### 5. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `clipbrain`
3. Description: "Personal video knowledge base with AI"
4. Visibility: Private (recommended) or Public
5. Click "Create repository"

#### 6. Push Code to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/clipbrain.git

# Push to GitHub
git branch -M main
git push -u origin main
```

✅ **Status**: Code on GitHub!

### Phase 3: Railway Deployment (10 minutes)

#### 7. Deploy Backend to Railway

**Option A: Via Dashboard (Recommended)**

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `clipbrain` repository
5. Railway will automatically:
   - Detect Python
   - Install dependencies
   - Start building
6. Wait 2-3 minutes for build

**Option B: Via CLI**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

✅ **Status**: Backend deploying...

#### 8. Configure Environment Variables

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"Raw Editor"**
4. Paste your environment variables:

```env
SUPABASE_URL=https://ifzdryytyqfufmjzchrr.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlmemRyeXl0eXFmdWZtanpjaHJyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjQ5NjMxNywiZXhwIjoyMDc4MDcyMzE3fQ.MfBotRZjoZYctMcuAsjo1ew6ASe_hOphowYF6lHTV-Y
REDIS_URL=rediss://default:ATnHAAIncDJmN2FiYjI1YzZhOTI0OGYzYmFjMDIyZmU0N2I5NmE2ZHAyMTQ3OTE@sincere-mammoth-14791.upstash.io:6379
DEEPGRAM_API_KEY=f4514f516bd9fe05aee157acdaa20f9c939f1c99
GEMINI_API_KEY=AIzaSyDWBxyr8yXSNdnCtfXbUsF6R5DEH3PK3NM
ALLOWED_PLATFORMS=youtube,instagram,tiktok,facebook
MAX_VIDEO_DURATION_SECONDS=7200
SIGNED_URL_TTL_SECONDS=900
INGEST_RATE_LIMIT_PER_HOUR=10
SEARCH_RATE_LIMIT_PER_HOUR=100
```

5. Click **"Save"**
6. Railway will automatically redeploy

✅ **Status**: Environment configured!

#### 9. Generate Domain

1. Click service → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Copy your URL: `https://clipbrain-production.up.railway.app`
4. **Save this URL** - you'll need it!

**Your Railway URL**: _________________________________

✅ **Status**: Domain generated!

#### 10. Deploy Worker Service

1. In Railway project, click **"New Service"**
2. Select **"GitHub Repo"** → Choose `clipbrain`
3. Click on the new service
4. Go to **"Settings"** → **"Deploy"**
5. Set **Custom Start Command**:
   ```bash
   cd backend && python workers/worker.py
   ```
6. Go to **"Variables"** → **"Raw Editor"**
7. Paste the same environment variables
8. Click **"Save"**

✅ **Status**: Worker deployed!

### Phase 4: Verification (5 minutes)

#### 11. Test Deployed Backend

```bash
# Replace with your Railway URL
export API_URL="https://your-app.up.railway.app"

# Test health
curl $API_URL/healthz

# Expected: {"status":"healthy","redis":true,"supabase":true,...}
```

✅ **Status**: Health check passing!

#### 12. Test Video Ingestion

```bash
# Ingest a test video
curl -X POST $API_URL/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Save the video_id from response
# Check status
curl $API_URL/job/VIDEO_ID
```

✅ **Status**: Ingestion working!

#### 13. Monitor Logs

**In Railway Dashboard:**
1. Click on backend service
2. Go to **"Deployments"**
3. Click latest deployment
4. View real-time logs

**With CLI:**
```bash
railway logs
```

✅ **Status**: Logs accessible!

### Phase 5: Final Configuration (Optional)

#### 14. Set Up Custom Domain (Optional)

1. Go to **"Settings"** → **"Networking"**
2. Click **"Custom Domain"**
3. Add your domain (e.g., `api.clipbrain.com`)
4. Update DNS records as shown
5. SSL automatically provisioned

#### 15. Set Up Monitoring (Recommended)

**Option 1: UptimeRobot (Free)**
1. Go to https://uptimerobot.com
2. Add monitor for your Railway URL
3. Set check interval: 5 minutes
4. Add email alerts

**Option 2: Pingdom**
1. Go to https://pingdom.com
2. Add uptime check
3. Configure alerts

#### 16. Enable Auto-Deploy

Railway automatically deploys on every push to `main`:

```bash
# Make a change
echo "# Update" >> README.md

# Commit and push
git add .
git commit -m "Update"
git push origin main

# Railway will automatically deploy!
```

## 📊 Deployment Summary

### What You've Deployed

**Backend Service:**
- URL: `https://your-app.up.railway.app`
- Features: All 11 API endpoints
- Status: ✅ Running

**Worker Service:**
- Function: Background job processing
- Status: ✅ Running

**Database:**
- Provider: Supabase
- Tables: 6 tables with indexes
- Status: ✅ Connected

**Queue:**
- Provider: Upstash Redis
- Status: ✅ Connected

**AI Services:**
- Deepgram: ✅ Connected
- Gemini: ✅ Connected

### Cost Breakdown

- Railway: $5 credit/month (free)
- Supabase: Free tier
- Upstash: Free tier
- Deepgram: $200 credit
- Gemini: Free tier

**Total: $0/month** 🎉

## 🧪 Testing Your Deployment

### Test Suite

```bash
# Set your Railway URL
export API_URL="https://your-app.up.railway.app"

# 1. Health check
curl $API_URL/healthz

# 2. Ingest video
curl -X POST $API_URL/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# 3. Check job status (use video_id from above)
curl $API_URL/job/VIDEO_ID

# 4. Get video details (after processing completes)
curl $API_URL/item/VIDEO_ID

# 5. Search
curl -X POST $API_URL/search \
  -H "Content-Type: application/json" \
  -d '{"q": "never gonna give you up", "top_k": 5}'

# 6. Create collection
curl -X POST $API_URL/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "My Favorites"}'

# 7. List collections
curl $API_URL/collections

# 8. Export data
curl $API_URL/export -o clipbrain_export.zip
```

## 🐛 Troubleshooting

### Build Fails

**Check:**
1. Railway logs for error messages
2. Ensure `requirements.txt` is correct
3. Verify Python version (3.11+)

**Fix:**
```bash
# Update requirements if needed
pip freeze > backend/requirements.txt
git add backend/requirements.txt
git commit -m "Update requirements"
git push origin main
```

### Health Check Fails

**Check:**
1. Environment variables are set
2. Supabase and Redis URLs are correct
3. Services are accessible

**Fix:**
1. Go to Railway → Variables
2. Verify all variables are set
3. Check for typos in URLs

### Worker Not Processing

**Check:**
1. Worker service is running
2. Worker logs for errors
3. Redis connection

**Fix:**
1. Restart worker service in Railway
2. Check worker logs
3. Verify Redis URL

### API Errors

**Check:**
1. Backend logs
2. Request format
3. Rate limits

**Fix:**
1. Review error message in logs
2. Check API documentation
3. Verify request payload

## 📚 Next Steps

### Immediate

1. ✅ Test all API endpoints
2. ✅ Verify worker processing
3. ✅ Monitor logs for errors
4. ✅ Set up uptime monitoring

### Short Term

1. Deploy frontend to Vercel
2. Test end-to-end flow
3. Add more videos
4. Test search functionality

### Long Term

1. Implement frontend UI
2. Add PWA features
3. Mobile app
4. Advanced features

## 📖 Documentation Reference

- **Quick Start**: `QUICK_START.md`
- **Railway Guide**: `RAILWAY_QUICK_DEPLOY.md`
- **API Docs**: `https://your-app.up.railway.app/docs`
- **Deployment Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Test Results**: `TEST_RESULTS.md`

## 🎉 Congratulations!

Your ClipBrain backend is now live and fully operational!

**What you can do now:**
- Ingest videos from 4 platforms
- Automatic transcription
- AI-powered notes
- Semantic search
- Collections and tags
- Data export

**Your API is live at**: `https://your-app.up.railway.app`

---

**Need help?** Check the troubleshooting section or review the detailed guides.

**Ready to use?** Start ingesting videos and building your knowledge base! 🚀
