"""Tag management routes."""

from fastapi import APIRouter, HTTPException
from models import UpdateTagsRequest
from supabase_client import supabase

router = APIRouter()


@router.patch("/item/{video_id}/tags")
async def update_tags(video_id: str, request: UpdateTagsRequest):
    """
    Update video tags/keywords.
    
    Args:
        video_id: Video ID
        request: Tags update request
    
    Returns:
        Success message
    """
    # Check video exists
    video = await supabase.select(
        "videos",
        columns="id",
        filters={"id": video_id},
        limit=1
    )
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Update keywords in notes table
    await supabase.update(
        "notes",
        {"keywords": request.keywords},
        {"video_id": video_id}
    )
    
    return {"message": "Tags updated successfully"}
