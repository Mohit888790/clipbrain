"""Ingestion routes."""

from fastapi import APIRouter, HTTPException
from models import IngestRequest, IngestResponse
from services.url_utils import URLUtils
from supabase_client import supabase
from workers.job_queue import enqueue_job
from workers.pipeline import process_video
from config import settings

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_video(request: IngestRequest):
    """
    Ingest a video URL.
    
    Args:
        request: Ingest request with URL
    
    Returns:
        Job ID and video ID
    """
    # Validate URL
    if not URLUtils.is_valid_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Detect platform
    platform = URLUtils.detect_platform(request.url)
    if not platform:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    
    # Validate platform is allowed
    if not URLUtils.validate_platform(platform, settings.allowed_platforms_list):
        raise HTTPException(
            status_code=400,
            detail=f"Platform '{platform}' is not supported. Allowed: {settings.allowed_platforms}"
        )
    
    # Canonicalize URL
    canonical_url = URLUtils.canonicalize_url(request.url, platform)
    url_hash = URLUtils.generate_url_hash(canonical_url)
    
    # Check for duplicates
    existing = await supabase.select(
        "videos",
        columns="id,status",
        filters={"canonical_url_hash": url_hash},
        limit=1
    )
    
    if existing:
        video = existing[0]
        if video["status"] == "done":
            # Already processed
            return IngestResponse(
                job_id="existing",
                video_id=video["id"]
            )
        elif video["status"] in ["queued", "processing"]:
            # Already in progress
            return IngestResponse(
                job_id="in_progress",
                video_id=video["id"]
            )
        # If failed, allow retry by creating new job
    
    # Create video record
    video_data = {
        "source_url": request.url,
        "canonical_url_hash": url_hash,
        "platform": platform,
        "status": "queued",
    }
    
    created = await supabase.insert("videos", video_data)
    video_id = created[0]["id"]
    
    # Enqueue job
    job = enqueue_job(process_video, video_id, canonical_url)
    
    return IngestResponse(
        job_id=job.id,
        video_id=video_id
    )
