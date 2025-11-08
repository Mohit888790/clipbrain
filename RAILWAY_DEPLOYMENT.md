# ClipBrain - Railway Deployment Guide

## 🚂 Deploy to Railway in 10 Minutes

Railway is a modern deployment platform that makes it easy to deploy your backend with zero configuration.

## Prerequisites

- ✅ Railway account (you have this)
- ✅ Environment variables configured (you have this)
- ✅ GitHub repository (optional but recommended)

## Deployment Options

### Option 1: Deploy from GitHub (Recommended) ⭐

This is the easiest method - Railway auto-deploys on every push.

#### Step 1: Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/clipbrain.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy Backend on Railway

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `clipbrain` repository
5. Railway will auto-detect Python and start building
6. Wait for deployment to complete (~2-3 minutes)

#### Step 3: Configure Environment Variables

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"Add Variable"** and add each one:

```bash
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

4. Railway will automatically redeploy with new variables

#### Step 4: Deploy Worker (Separate Service)

1. In your Railway project, click **"New Service"**
2. Select **"GitHub Repo"** → Choose same repository
3. Click on the new service
4. Go to **"Settings"** → **"Deploy"**
5. Set **Custom Start Command**:
   ```bash
   cd backend && python workers/worker.py
   ```
6. Go to **"Variables"** and add the same environment variables
7. Deploy!

#### Step 5: Get Your API URL

1. Click on your backend service
2. Go to **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Copy your URL: `https://clipbrain-api-production.up.railway.app`

### Option 2: Deploy with Railway CLI

If you prefer command line:

#### Step 1: Install Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Or with npm
npm i -g @railway/cli
```

#### Step 2: Login and Initialize

```bash
# Login to Railway
railway login

# Link to your project (or create new)
railway link

# Or create new project
railway init
```

#### Step 3: Deploy Backend

```bash
# Deploy
railway up

# Set environment variables
railway variables set SUPABASE_URL="https://ifzdryytyqfufmjzchrr.supabase.co"
railway variables set SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlmemRyeXl0eXFmdWZtanpjaHJyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjQ5NjMxNywiZXhwIjoyMDc4MDcyMzE3fQ.MfBotRZjoZYctMcuAsjo1ew6ASe_hOphowYF6lHTV-Y"
railway variables set REDIS_URL="rediss://default:ATnHAAIncDJmN2FiYjI1YzZhOTI0OGYzYmFjMDIyZmU0N2I5NmE2ZHAyMTQ3OTE@sincere-mammoth-14791.upstash.io:6379"
railway variables set DEEPGRAM_API_KEY="f4514f516bd9fe05aee157acdaa20f9c939f1c99"
railway variables set GEMINI_API_KEY="AIzaSyDWBxyr8yXSNdnCtfXbUsF6R5DEH3PK3NM"
railway variables set ALLOWED_PLATFORMS="youtube,instagram,tiktok,facebook"
railway variables set MAX_VIDEO_DURATION_SECONDS="7200"
railway variables set SIGNED_URL_TTL_SECONDS="900"
railway variables set INGEST_RATE_LIMIT_PER_HOUR="10"
railway variables set SEARCH_RATE_LIMIT_PER_HOUR="100"

# Open in browser
railway open
```

#### Step 4: Deploy Worker

```bash
# Create new service for worker
railway service create clipbrain-worker

# Switch to worker service
railway service

# Set start command
railway run cd backend && python workers/worker.py

# Set same environment variables
railway variables set SUPABASE_URL="..." (repeat all variables)
```

## Verify Deployment

### Check Backend Health

```bash
# Get your Railway URL from dashboard
curl https://your-app.up.railway.app/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "redis": true,
  "supabase": true,
  "timestamp": "2025-11-08T..."
}
```

### Test Ingestion

```bash
curl -X POST https://your-app.up.railway.app/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### View Logs

**In Dashboard:**
1. Click on your service
2. Go to **"Deployments"** tab
3. Click on latest deployment
4. View logs in real-time

**With CLI:**
```bash
railway logs
```

## Configuration Files

Railway uses these files (already created):

- ✅ `railway.json` - Railway configuration
- ✅ `railway.toml` - Alternative config format
- ✅ `Procfile` - Process definitions
- ✅ `backend/requirements.txt` - Python dependencies
- ✅ `backend/Dockerfile` - Container definition (optional)

## Railway Features

### Auto-Deploy on Push
- Every push to `main` branch triggers automatic deployment
- No manual intervention needed
- Rollback available if needed

### Environment Variables
- Securely stored and encrypted
- Can be shared across services
- Easy to update in dashboard

### Monitoring
- Real-time logs
- Deployment history
- Resource usage metrics
- Health checks

### Scaling
- Vertical scaling (increase resources)
- Horizontal scaling (multiple instances)
- Auto-restart on failure

## Troubleshooting

### Build Fails

**Issue**: `ModuleNotFoundError`
**Fix**: Ensure all dependencies are in `backend/requirements.txt`

**Issue**: `No module named 'config'`
**Fix**: Check that start command includes `cd backend`

### Deployment Succeeds but App Crashes

**Check logs:**
```bash
railway logs
```

**Common issues:**
- Missing environment variables
- Wrong start command
- Port binding (use `$PORT` variable)

### Worker Not Processing Jobs

**Check:**
1. Worker service is running (check Railway dashboard)
2. Redis URL is correct
3. Worker logs for errors:
   ```bash
   railway logs --service clipbrain-worker
   ```

### Health Check Fails

**Check:**
1. Supabase URL and key are correct
2. Redis URL is accessible
3. All environment variables are set

## Cost & Limits

### Free Tier ($5 credit/month)
- Enough for small projects
- ~500 hours of runtime
- 100 GB bandwidth
- Shared CPU

### Usage Monitoring
- Check usage in Railway dashboard
- Set up billing alerts
- Monitor credit consumption

### Optimization Tips
1. **Use worker efficiently** - Process jobs in batches
2. **Cache results** - Reduce API calls
3. **Optimize images** - Use smaller Docker base
4. **Monitor logs** - Catch issues early

## Advanced Configuration

### Custom Domain

1. Go to **"Settings"** → **"Networking"**
2. Click **"Custom Domain"**
3. Add your domain
4. Update DNS records as shown
5. SSL automatically provisioned

### Database Backups

Railway doesn't backup your Supabase data. Use Supabase's built-in backups:
1. Go to Supabase dashboard
2. **Database** → **Backups**
3. Enable automatic backups

### Monitoring & Alerts

1. Set up health check endpoint: `/healthz`
2. Use external monitoring (UptimeRobot, Pingdom)
3. Set up alerts for downtime

## Deployment Checklist

- [x] Railway account created
- [x] Environment variables configured
- [ ] Backend deployed
- [ ] Worker deployed
- [ ] Health check passing
- [ ] Test ingestion endpoint
- [ ] Test search endpoint
- [ ] Update frontend API URL
- [ ] Test end-to-end flow
- [ ] Set up monitoring
- [ ] Configure custom domain (optional)

## Next Steps

1. **Deploy Backend** - Follow Option 1 or 2 above
2. **Deploy Worker** - Create separate service
3. **Test Thoroughly** - Use all endpoints
4. **Deploy Frontend** - Update API URL to Railway
5. **Monitor** - Check logs and metrics

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app

## Comparison: Railway vs Fly.io

| Feature | Railway | Fly.io |
|---------|---------|--------|
| Free Tier | $5 credit/month | 3 VMs free |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GitHub Integration | ✅ Built-in | ❌ Manual |
| Auto-Deploy | ✅ Yes | ❌ No |
| Dashboard | ⭐⭐⭐⭐⭐ Modern | ⭐⭐⭐ Basic |
| Logs | ⭐⭐⭐⭐⭐ Real-time | ⭐⭐⭐⭐ Good |
| Pricing | Simple | Complex |

**Winner**: Railway for ease of use and developer experience! 🚂

---

**Ready to deploy? Start with Option 1 (GitHub) - it's the easiest!** 🚀
