# ClipBrain - Alternative Deployment Options

## 🚀 Railway Deployment (Recommended)

### Why Railway?
- ✅ $5 free credit per month
- ✅ Similar to Fly.io (easy migration)
- ✅ Auto-deploy from GitHub
- ✅ Simple environment variables
- ✅ Built-in logging and metrics
- ✅ Automatic HTTPS

### Step-by-Step Railway Deployment

#### 1. Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Get $5 free credit/month

#### 2. Deploy Backend

**Option A: Using Railway CLI**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add environment variables
railway variables set SUPABASE_URL="https://..."
railway variables set SUPABASE_SERVICE_KEY="..."
railway variables set REDIS_URL="rediss://..."
railway variables set DEEPGRAM_API_KEY="..."
railway variables set GEMINI_API_KEY="..."
railway variables set ALLOWED_PLATFORMS="youtube,instagram,tiktok,facebook"
railway variables set MAX_VIDEO_DURATION_SECONDS="7200"
railway variables set SIGNED_URL_TTL_SECONDS="900"
railway variables set INGEST_RATE_LIMIT_PER_HOUR="10"
railway variables set SEARCH_RATE_LIMIT_PER_HOUR="100"
```

**Option B: Using GitHub (Easier)**
1. Push code to GitHub
2. Go to Railway dashboard
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway auto-detects Python and deploys
7. Add environment variables in Settings → Variables
8. Deploy!

#### 3. Deploy Worker (Separate Service)
1. In Railway dashboard, click "New Service"
2. Select same GitHub repo
3. In Settings → Deploy, set start command:
   ```
   cd backend && python workers/worker.py
   ```
4. Use same environment variables
5. Deploy!

#### 4. Get Your URL
- Railway provides: `https://your-app.up.railway.app`
- Use this as your `NEXT_PUBLIC_API_URL` for frontend

### Railway Configuration Files
- ✅ `railway.json` - Railway config
- ✅ `railway.toml` - Alternative config
- ✅ `Procfile` - Process definitions

---

## 🎨 Render Deployment

### Why Render?
- ✅ 750 hours/month free
- ✅ Auto-deploy from GitHub
- ✅ Free PostgreSQL and Redis
- ✅ Built-in cron jobs
- ✅ Automatic SSL

### Step-by-Step Render Deployment

#### 1. Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

#### 2. Deploy Backend
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Configure:
   - **Name**: clipbrain-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Click "Create Web Service"

#### 3. Deploy Worker
1. Click "New +" → "Background Worker"
2. Select same repository
3. Configure:
   - **Name**: clipbrain-worker
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python workers/worker.py`
4. Use same environment variables
5. Click "Create Background Worker"

#### 4. Get Your URL
- Render provides: `https://clipbrain-api.onrender.com`

### Render Configuration
Create `render.yaml`:
```yaml
services:
  - type: web
    name: clipbrain-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: REDIS_URL
        sync: false
      - key: DEEPGRAM_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false

  - type: worker
    name: clipbrain-worker
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && python workers/worker.py
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: REDIS_URL
        sync: false
      - key: DEEPGRAM_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
```

---

## 🟣 Heroku Deployment

### Why Heroku?
- ✅ Most mature platform
- ✅ Extensive documentation
- ✅ Large ecosystem
- ✅ Easy scaling

### Step-by-Step Heroku Deployment

#### 1. Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. Deploy
```bash
# Login
heroku login

# Create app
heroku create clipbrain-api

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set SUPABASE_URL="https://..."
heroku config:set SUPABASE_SERVICE_KEY="..."
heroku config:set REDIS_URL="rediss://..."
heroku config:set DEEPGRAM_API_KEY="..."
heroku config:set GEMINI_API_KEY="..."
heroku config:set ALLOWED_PLATFORMS="youtube,instagram,tiktok,facebook"
heroku config:set MAX_VIDEO_DURATION_SECONDS="7200"
heroku config:set SIGNED_URL_TTL_SECONDS="900"
heroku config:set INGEST_RATE_LIMIT_PER_HOUR="10"
heroku config:set SEARCH_RATE_LIMIT_PER_HOUR="100"

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

#### 3. Get Your URL
- Heroku provides: `https://clipbrain-api.herokuapp.com`

### Heroku Configuration
The `Procfile` is already created:
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
worker: cd backend && python workers/worker.py
```

---

## 🌊 DigitalOcean App Platform

### Why DigitalOcean?
- ✅ $200 free credit (60 days)
- ✅ Simple pricing after free tier
- ✅ Good performance
- ✅ Managed databases

### Step-by-Step DigitalOcean Deployment

#### 1. Create Account
1. Go to https://www.digitalocean.com
2. Sign up and get $200 credit

#### 2. Deploy
1. Go to Apps → Create App
2. Connect GitHub repository
3. Configure:
   - **Type**: Web Service
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Run Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Choose $5/month plan (covered by credit)
6. Deploy!

#### 3. Add Worker
1. Add Component → Worker
2. Configure:
   - **Run Command**: `cd backend && python workers/worker.py`
3. Use same environment variables

---

## ☁️ Google Cloud Run

### Why Cloud Run?
- ✅ Pay only for what you use
- ✅ Scales to zero
- ✅ 2 million requests/month free
- ✅ $300 free credit

### Step-by-Step Cloud Run Deployment

#### 1. Install gcloud CLI
```bash
# Follow instructions at:
# https://cloud.google.com/sdk/docs/install
```

#### 2. Deploy
```bash
# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy clipbrain-api \
  --source backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Set environment variables
gcloud run services update clipbrain-api \
  --set-env-vars SUPABASE_URL="...",REDIS_URL="..."
```

---

## 📊 Cost Comparison

| Platform | Free Tier | After Free | Best For |
|----------|-----------|------------|----------|
| **Railway** | $5/month credit | $0.000463/GB-hour | Quick start |
| **Render** | 750 hrs/month | $7/month | Free hosting |
| **Heroku** | 550-1000 hrs | $7/month | Mature apps |
| **DigitalOcean** | $200 credit | $5/month | Simple pricing |
| **Cloud Run** | 2M req/month | Pay per use | Serverless |

## 🎯 Recommendation by Use Case

### For Quick Testing
→ **Railway** or **Render** (easiest setup)

### For Long-term Free Hosting
→ **Render** (750 hours/month)

### For Production
→ **Railway** or **DigitalOcean** (reliable, good support)

### For Serverless
→ **Google Cloud Run** (scales to zero)

### For Enterprise
→ **AWS** or **Azure** (full ecosystem)

## 🔧 Migration from Fly.io

If you're already on Fly.io and want to migrate:

1. **Export environment variables**:
   ```bash
   fly secrets list
   ```

2. **Choose new platform** (Railway recommended)

3. **Deploy to new platform** using guides above

4. **Update frontend** `NEXT_PUBLIC_API_URL`

5. **Test thoroughly**

6. **Delete Fly.io app**:
   ```bash
   fly apps destroy clipbrain-api
   ```

## 💡 Tips

- **Railway**: Best for quick deployment, similar to Fly.io
- **Render**: Best for free tier, auto-sleep is fine for personal use
- **Heroku**: Best for mature projects, extensive add-ons
- **DigitalOcean**: Best for predictable pricing
- **Cloud Run**: Best for variable traffic, pay per use

## 🆘 Troubleshooting

### Port Issues
Most platforms set `$PORT` automatically. Make sure your start command uses it:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Build Failures
- Ensure `requirements.txt` is in root or specify path
- Check Python version (3.11+ required)
- Verify all dependencies are listed

### Worker Not Running
- Deploy worker as separate service/dyno
- Ensure Redis URL is accessible
- Check worker logs for errors

---

**Recommended: Start with Railway for easiest migration from Fly.io!** 🚀
