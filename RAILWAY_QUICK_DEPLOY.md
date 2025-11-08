# 🚂 Deploy ClipBrain to Railway - Quick Guide

Since you already have a Railway account and environment variables configured, here's the fastest way to deploy:

## 🚀 Deploy in 3 Steps (5 minutes)

### Step 1: Push to GitHub (if not already done)

```bash
# Initialize git
git init
git add .
git commit -m "ClipBrain initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/clipbrain.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend on Railway

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `clipbrain` repository
5. Railway will automatically:
   - Detect Python
   - Install dependencies from `backend/requirements.txt`
   - Start the server using `railway.json` config
6. Wait 2-3 minutes for build to complete

### Step 3: Add Your Environment Variables

Click on your deployed service → **"Variables"** tab → **"Raw Editor"**

Paste this (your actual values):

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

Click **"Save"** - Railway will automatically redeploy.

## ✅ Verify Deployment

### Get Your URL

1. Click on your service
2. Go to **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Copy your URL (e.g., `https://clipbrain-production.up.railway.app`)

### Test It

```bash
# Replace with your Railway URL
export API_URL="https://your-app.up.railway.app"

# Health check
curl $API_URL/healthz

# Should return:
# {"status":"healthy","redis":true,"supabase":true,"timestamp":"..."}
```

## 🔧 Deploy Worker (Separate Service)

The worker processes videos in the background.

### Option 1: Deploy Worker on Railway

1. In your Railway project, click **"New Service"**
2. Select **"GitHub Repo"** → Choose same `clipbrain` repository
3. Click on the new service
4. Go to **"Settings"** → **"Deploy"**
5. Under **"Custom Start Command"**, enter:
   ```bash
   cd backend && python workers/worker.py
   ```
6. Go to **"Variables"** → **"Raw Editor"**
7. Paste the same environment variables as backend
8. Click **"Save"** - Worker will deploy!

### Option 2: Run Worker Locally (For Testing)

```bash
# In your local terminal
cd backend
python workers/worker.py
```

This works fine for testing since the worker connects to the same Redis queue.

## 📊 Monitor Your Deployment

### View Logs

**In Dashboard:**
1. Click on your service
2. Go to **"Deployments"** tab
3. Click latest deployment
4. View real-time logs

**With CLI:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs
```

### Check Resource Usage

1. Click on your service
2. Go to **"Metrics"** tab
3. View CPU, memory, network usage

## 🧪 Test Your Deployed API

```bash
# Set your Railway URL
export API_URL="https://your-app.up.railway.app"

# Test ingestion
curl -X POST $API_URL/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Response: {"job_id":"...","video_id":"..."}

# Check job status (use video_id from above)
curl $API_URL/job/VIDEO_ID

# Get video details
curl $API_URL/item/VIDEO_ID
```

## 🎯 Next Steps

### 1. Update Frontend

If you have a frontend, update the API URL:

```bash
# In frontend/.env.local
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

### 2. Set Up Custom Domain (Optional)

1. Go to **"Settings"** → **"Networking"**
2. Click **"Custom Domain"**
3. Add your domain (e.g., `api.clipbrain.com`)
4. Update DNS records as shown
5. SSL automatically provisioned!

### 3. Enable Auto-Deploy

Railway automatically deploys on every push to `main` branch. To deploy:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway will automatically build and deploy!

## 🐛 Troubleshooting

### Build Fails

**Check logs in Railway dashboard**

Common issues:
- Missing dependencies in `requirements.txt`
- Wrong Python version
- Path issues (ensure start command has `cd backend`)

### App Crashes After Deploy

**Check logs:**
```bash
railway logs
```

Common issues:
- Missing environment variables
- Wrong Redis URL format
- Database connection issues

### Worker Not Processing

**Check:**
1. Worker service is running (Railway dashboard)
2. Worker logs for errors
3. Redis connection is working

### Health Check Fails

**Verify:**
1. All environment variables are set
2. Supabase and Redis URLs are correct
3. Services are accessible from Railway

## 💰 Cost Monitoring

### Check Usage

1. Go to Railway dashboard
2. Click on your project
3. View **"Usage"** tab
4. Monitor credit consumption

### Free Tier Limits

- $5 credit per month
- ~500 hours of runtime
- 100 GB bandwidth

**Tip**: For personal use, this is usually enough!

## 📚 Helpful Commands

```bash
# View all services
railway status

# Restart service
railway restart

# Open dashboard
railway open

# View environment variables
railway variables

# Run command in Railway environment
railway run python backend/test_connections.py
```

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed on Railway
- [ ] Environment variables added
- [ ] Domain generated
- [ ] Health check passing
- [ ] Worker deployed (or running locally)
- [ ] Test ingestion endpoint
- [ ] Test search endpoint
- [ ] Update frontend API URL
- [ ] Test end-to-end flow

## 🎉 You're Done!

Your ClipBrain backend is now live on Railway!

**Your API is available at**: `https://your-app.up.railway.app`

**Next**: Deploy your frontend to Vercel and connect it to your Railway backend.

---

**Need help?** Check `RAILWAY_DEPLOYMENT.md` for detailed documentation.
