# 🔧 Railway Deployment Fix

## Issue: Redis URL Not Found

The deployment is failing because environment variables aren't set in Railway.

## Quick Fix (5 minutes)

### Step 1: Go to Railway Dashboard

1. Open https://railway.app/dashboard
2. Click on your `clipbrain` project
3. Click on your service (the one that's failing)

### Step 2: Add Environment Variables

1. Click on **"Variables"** tab
2. Click **"Raw Editor"** button
3. **Copy and paste this EXACTLY**:

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

4. Click **"Save"** or **"Update Variables"**

### Step 3: Redeploy

Railway will automatically redeploy after you save the variables.

**Wait 2-3 minutes** for the build to complete.

### Step 4: Verify

Once deployed, check the logs:
1. Click on **"Deployments"** tab
2. Click on the latest deployment
3. Look for: "🚀 Starting ClipBrain API..."
4. Should see: "✅ Application started successfully"

### Step 5: Test

Get your Railway URL:
1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"** if not already done
3. Copy your URL

Test it:
```bash
curl https://your-app.up.railway.app/healthz
```

Should return:
```json
{"status":"healthy","redis":true,"supabase":true,"timestamp":"..."}
```

## Alternative: Use Railway CLI

If you prefer command line:

```bash
# Login
railway login

# Link to your project
railway link

# Set variables one by one
railway variables set REDIS_URL="rediss://default:ATnHAAIncDJmN2FiYjI1YzZhOTI0OGYzYmFjMDIyZmU0N2I5NmE2ZHAyMTQ3OTE@sincere-mammoth-14791.upstash.io:6379"
railway variables set SUPABASE_URL="https://ifzdryytyqfufmjzchrr.supabase.co"
railway variables set SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlmemRyeXl0eXFmdWZtanpjaHJyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjQ5NjMxNywiZXhwIjoyMDc4MDcyMzE3fQ.MfBotRZjoZYctMcuAsjo1ew6ASe_hOphowYF6lHTV-Y"
railway variables set DEEPGRAM_API_KEY="f4514f516bd9fe05aee157acdaa20f9c939f1c99"
railway variables set GEMINI_API_KEY="AIzaSyDWBxyr8yXSNdnCtfXbUsF6R5DEH3PK3NM"
railway variables set ALLOWED_PLATFORMS="youtube,instagram,tiktok,facebook"
railway variables set MAX_VIDEO_DURATION_SECONDS="7200"
railway variables set SIGNED_URL_TTL_SECONDS="900"
railway variables set INGEST_RATE_LIMIT_PER_HOUR="10"
railway variables set SEARCH_RATE_LIMIT_PER_HOUR="100"

# Redeploy
railway up
```

## Why This Happened

Railway needs environment variables to be explicitly set in the dashboard or via CLI. The `.env` file in your repository is not automatically used (for security reasons).

## Next Steps

After fixing:
1. ✅ Backend should deploy successfully
2. ✅ Health check should pass
3. ✅ Test ingestion endpoint
4. ✅ Deploy worker service (separate service with same variables)

---

**This should fix the deployment!** The error was simply missing environment variables in Railway.
