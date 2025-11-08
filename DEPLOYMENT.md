# ClipBrain Deployment Guide

## Backend Deployment (Railway) ⭐ Recommended

### Prerequisites

1. Railway account (free - get $5 credit/month)
2. GitHub account (optional but recommended)

### Quick Deploy (5 minutes)

#### Option 1: Deploy from GitHub (Easiest)

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/clipbrain.git
git push -u origin main
```

2. **Deploy on Railway**:
   - Go to https://railway.app/dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects and deploys!

3. **Add Environment Variables**:
   - Click on your service → "Variables"
   - Add all variables from your `.env` file:
     ```
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

4. **Deploy Worker** (separate service):
   - Click "New Service" → Select same repo
   - Go to Settings → Deploy
   - Set start command: `cd backend && python workers/worker.py`
   - Add same environment variables

5. **Get Your URL**:
   - Click service → Settings → Networking
   - Click "Generate Domain"
   - Copy URL: `https://your-app.up.railway.app`

#### Option 2: Deploy with CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up

# Set environment variables (or use dashboard)
railway variables set SUPABASE_URL="https://ifzdryytyqfufmjzchrr.supabase.co"
# ... (add all variables)

# View logs
railway logs
```

## Frontend Deployment (Vercel)

### Prerequisites

1. Install Vercel CLI:
```bash
npm i -g vercel
```

### Deploy Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Deploy:
```bash
vercel
```

4. Set environment variable in Vercel dashboard:
- `NEXT_PUBLIC_API_URL`: Your Fly.io backend URL (e.g., `https://clipbrain-api.fly.dev`)

5. Redeploy:
```bash
vercel --prod
```

## Alternative: Fly.io Deployment

If you prefer Fly.io over Railway:

### Backend on Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Deploy: `fly launch` (in backend directory)
4. Set secrets: `fly secrets set KEY=value`
5. Deploy: `fly deploy`

### Worker on Fly.io

1. Create `fly.worker.toml` with worker configuration
2. Deploy: `fly deploy -c fly.worker.toml`

**Note**: Railway is recommended for easier setup and better developer experience.

## Monitoring

### Railway

```bash
# View logs (CLI)
railway logs

# View logs (Dashboard)
# Click service → Deployments → View logs

# Check metrics
# Dashboard shows CPU, memory, network usage

# Restart service
railway restart
```

### Vercel

- View logs in Vercel dashboard
- Monitor analytics
- Check deployment status

## Troubleshooting

### Backend won't start

1. Check logs: `fly logs`
2. Verify environment variables: `fly secrets list`
3. Test locally with Docker:
```bash
docker build -t clipbrain-backend .
docker run -p 8000:8000 --env-file ../.env clipbrain-backend
```

### Worker not processing jobs

1. Check Redis connection
2. Verify worker is running: `fly status`
3. Check worker logs
4. Test job queue locally

### Database connection issues

1. Verify Supabase URL and key
2. Check if Supabase project is active
3. Test connection with verification script:
```bash
python backend/test_connections.py
```

## Cost Optimization

### Railway Free Tier

- $5 credit per month
- ~500 hours of runtime
- 100 GB bandwidth/month
- Shared CPU resources

### Vercel Free Tier

- 100 GB bandwidth/month
- Unlimited deployments
- Automatic HTTPS

### Tips

1. Use auto-stop for backend (already configured)
2. Implement caching for search results
3. Monitor API quotas (Deepgram, Gemini)
4. Use Supabase free tier limits wisely

## Security

1. Never commit `.env` files
2. Rotate API keys regularly
3. Use Fly.io secrets for sensitive data
4. Enable CORS only for your frontend domain
5. Monitor rate limits and adjust as needed

## Backup

1. Supabase auto-backups (daily)
2. Export data regularly via `/export` endpoint
3. Keep local copy of environment variables

## Next Steps

After deployment:

1. Test all endpoints
2. Verify worker is processing jobs
3. Test PWA installation on mobile
4. Monitor logs for errors
5. Set up alerts for failures
