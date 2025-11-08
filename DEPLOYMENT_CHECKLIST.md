# 🚂 Railway Deployment Checklist

Use this checklist to deploy ClipBrain to Railway.

## ✅ Pre-Deployment

- [x] Railway account created
- [x] Environment variables configured in `.env`
- [x] Database migrations run in Supabase
- [x] All services tested locally
- [ ] Code committed to Git
- [ ] GitHub repository created

## 📦 Prepare for Deployment

### 1. Push to GitHub

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Railway deployment"

# Create GitHub repo, then:
git remote add origin https://github.com/YOUR_USERNAME/clipbrain.git
git branch -M main
git push -u origin main
```

**Status**: [ ] Complete

## 🚀 Deploy Backend

### 2. Create Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose `clipbrain` repository
5. Wait for initial deployment (~2-3 minutes)

**Status**: [ ] Complete

### 3. Add Environment Variables

Click service → **"Variables"** → **"Raw Editor"**, paste:

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

Click **"Save"** - Railway will redeploy automatically.

**Status**: [ ] Complete

### 4. Generate Domain

1. Click service → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Copy your URL: `https://clipbrain-production.up.railway.app`
4. Save this URL - you'll need it for frontend

**Your Railway URL**: ___________________________________

**Status**: [ ] Complete

## 🔧 Deploy Worker

### 5. Create Worker Service

1. In Railway project, click **"New Service"**
2. Select **"GitHub Repo"** → Choose `clipbrain`
3. Click on new service
4. Go to **"Settings"** → **"Deploy"**
5. Set **Custom Start Command**:
   ```bash
   cd backend && python workers/worker.py
   ```
6. Go to **"Variables"** → **"Raw Editor"**
7. Paste same environment variables as backend
8. Click **"Save"**

**Status**: [ ] Complete

## ✅ Verify Deployment

### 6. Test Health Endpoint

```bash
# Replace with your Railway URL
curl https://your-app.up.railway.app/healthz
```

**Expected Response**:
```json
{
  "status": "healthy",
  "redis": true,
  "supabase": true,
  "timestamp": "..."
}
```

**Status**: [ ] Complete

### 7. Test Ingestion

```bash
curl -X POST https://your-app.up.railway.app/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Expected Response**:
```json
{
  "job_id": "...",
  "video_id": "..."
}
```

**Status**: [ ] Complete

### 8. Check Job Status

```bash
# Use video_id from above
curl https://your-app.up.railway.app/job/VIDEO_ID
```

**Expected Response**:
```json
{
  "status": "processing",
  "video_id": "...",
  "current_stage": "download"
}
```

**Status**: [ ] Complete

### 9. Verify Worker Processing

1. Go to Railway dashboard
2. Click on worker service
3. Go to **"Deployments"** → View logs
4. Should see: "🚀 Starting ClipBrain worker..."

**Status**: [ ] Complete

## 📊 Monitor Deployment

### 10. Check Logs

**Backend Logs**:
1. Click backend service
2. Go to **"Deployments"**
3. Click latest deployment
4. View logs

**Worker Logs**:
1. Click worker service
2. Go to **"Deployments"**
3. View logs

**Status**: [ ] Complete

### 11. Monitor Resource Usage

1. Click on service
2. Go to **"Metrics"** tab
3. Check CPU, memory, network usage
4. Ensure within free tier limits

**Status**: [ ] Complete

## 🎨 Deploy Frontend (Optional)

### 12. Deploy to Vercel

1. Go to https://vercel.com
2. Click **"New Project"**
3. Import `clipbrain` repository
4. Set **Root Directory**: `frontend`
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
   ```
6. Deploy!

**Status**: [ ] Complete

## 🔒 Security & Optimization

### 13. Security Checklist

- [ ] Environment variables are set (not hardcoded)
- [ ] `.env` file is in `.gitignore`
- [ ] API keys are not exposed in logs
- [ ] CORS is configured properly
- [ ] Rate limiting is enabled

**Status**: [ ] Complete

### 14. Performance Optimization

- [ ] Health check endpoint responding
- [ ] Worker processing jobs
- [ ] Search queries under 1.5s
- [ ] No memory leaks in logs

**Status**: [ ] Complete

## 📈 Post-Deployment

### 15. Set Up Monitoring

- [ ] Bookmark Railway dashboard
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure email alerts for downtime
- [ ] Monitor credit usage in Railway

**Status**: [ ] Complete

### 16. Documentation

- [ ] Update README with Railway URL
- [ ] Document any custom configurations
- [ ] Share API documentation with team (if applicable)

**Status**: [ ] Complete

### 17. Backup Strategy

- [ ] Supabase automatic backups enabled
- [ ] Export data regularly via `/export` endpoint
- [ ] Keep local copy of environment variables
- [ ] Document recovery procedures

**Status**: [ ] Complete

## 🎉 Deployment Complete!

### Final Checklist

- [ ] Backend deployed and healthy
- [ ] Worker deployed and processing
- [ ] All environment variables set
- [ ] Domain generated
- [ ] Health check passing
- [ ] Ingestion tested
- [ ] Search tested
- [ ] Logs reviewed
- [ ] Monitoring set up
- [ ] Documentation updated

## 📝 Deployment Information

**Deployment Date**: _______________

**Railway URLs**:
- Backend: ___________________________________
- Worker: ___________________________________

**Frontend URL** (if deployed): ___________________________________

**Notes**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

## 🆘 Troubleshooting

If something goes wrong:

1. **Check logs** in Railway dashboard
2. **Verify environment variables** are set correctly
3. **Test locally** to isolate issues
4. **Review** `TEST_RESULTS.md` for known issues
5. **Consult** `RAILWAY_DEPLOYMENT.md` for detailed guide

## 🎯 Next Steps

After successful deployment:

1. **Test all endpoints** thoroughly
2. **Monitor performance** for first 24 hours
3. **Set up alerts** for downtime
4. **Deploy frontend** if not done
5. **Share with users** (if applicable)

---

**Congratulations! Your ClipBrain backend is live on Railway!** 🚀
