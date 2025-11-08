"""Jump/deep link routes."""

from fastapi import APIRouter, HTTPException
from models import JumpResponse
from supabase_client import supabase
from storage import storage_service

router = APIRouter()


@router.get("/jump", response_model=JumpResponse)
async def generate_jump_link(video_id: str, start_ms: int):
    """
    Generate deep link and signed play URL.
    
    Args:
        video_id: Video ID
        start_ms: Start timestamp in milliseconds
    
    Returns:
        Deep link and signed play URL
    """
    # Get video
    video = await supabase.select(
        "videos",
        columns="source_url,platform,storage_path",
        filters={"id": video_id},
        limit=1
    )
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_data = video[0]
    start_seconds = start_ms / 1000
    
    # Generate deep link
    source_url = video_data["source_url"]
    platform = video_data["platform"]
    
    if platform == "youtube":
        separator = "&" if "?" in source_url else "?"
        deep_link = f"{source_url}{separator}t={int(start_seconds)}"
    else:
        deep_link = source_url
    
    # Generate signed play URL
    signed_play_url = ""
    if video_data.get("storage_path"):
        try:
            signed_play_url = await storage_service.generate_signed_url(
                video_data["storage_path"]
            )
        except Exception:
            pass
    
    return JumpResponse(
        deep_link=deep_link,
        signed_play_url=signed_play_url,
        start_seconds=start_seconds,
    )
