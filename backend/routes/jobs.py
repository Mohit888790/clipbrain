"""Job status routes."""

from fastapi import APIRouter, HTTPException
from models import JobStatusResponse
from supabase_client import supabase

router = APIRouter()


@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get job status.
    
    Args:
        job_id: Job ID or video ID
    
    Returns:
        Job status information
    """
    # Try to find video by ID (job_id might be video_id)
    video = await supabase.select(
        "videos",
        columns="id,status,fail_reason,current_stage",
        filters={"id": job_id},
        limit=1
    )
    
    if not video:
        raise HTTPException(status_code=404, detail="Job not found")
    
    video_data = video[0]
    
    return JobStatusResponse(
        status=video_data["status"],
        video_id=video_data["id"],
        fail_reason=video_data.get("fail_reason"),
        current_stage=video_data.get("current_stage"),
    )
