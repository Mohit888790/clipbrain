"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from config import settings
from database import db
from models import HealthResponse
from middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown."""
    # Startup
    print("🚀 Starting ClipBrain API...")
    # Note: Direct PostgreSQL connection disabled (using Supabase REST API instead)
    # await db.connect()
    print("✅ Application started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down ClipBrain API...")
    # await db.disconnect()
    print("✅ Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="ClipBrain API",
    description="Video ingestion and search API for ClipBrain",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.add_middleware(RateLimitMiddleware)


# Import routes
from routes import ingest, jobs, items, search, jump, export as export_route, collections, tags

# Include routers
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(jobs.router, tags=["Jobs"])
app.include_router(items.router, tags=["Items"])
app.include_router(search.router, tags=["Search"])
app.include_router(jump.router, tags=["Jump"])
app.include_router(export_route.router, tags=["Export"])
app.include_router(collections.router, tags=["Collections"])
app.include_router(tags.router, tags=["Tags"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ClipBrain API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    redis_healthy = False
    supabase_healthy = False
    
    # Check Redis connection
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        await r.close()
        redis_healthy = True
    except Exception as e:
        print(f"❌ Redis health check failed: {e}")
    
    # Check Supabase connection via REST API
    try:
        from supabase_client import supabase
        # Try to query videos table
        await supabase.select("videos", columns="id", limit=1)
        supabase_healthy = True
    except Exception as e:
        print(f"❌ Supabase health check failed: {e}")
    
    overall_status = "healthy" if (redis_healthy and supabase_healthy) else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        redis=redis_healthy,
        supabase=supabase_healthy,
        timestamp=datetime.utcnow(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
