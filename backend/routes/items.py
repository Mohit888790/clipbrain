"""Item/video detail routes."""

from fastapi import APIRouter, HTTPException
from models import ItemResponse, VideoDetails, NotesDetails, TranscriptChunk
from supabase_client import supabase
from storage import storage_service

router = APIRouter()


@router.get("/item/{video_id}", response_model=ItemResponse)
async def get_item(video_id: str):
    """
    Get video item details.
    
    Args:
        video_id: Video ID
    
    Returns:
        Complete video details with notes and transcript preview
    """
    # Get video
    video = await supabase.select(
        "videos",
        columns="*",
        filters={"id": video_id},
        limit=1
    )
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_data = video[0]
    
    # Generate signed URL for storage
    storage_url = None
    if video_data.get("storage_path"):
        try:
            storage_url = await storage_service.generate_signed_url(
                video_data["storage_path"]
            )
        except Exception:
            pass
    
    # Get notes
    notes = await supabase.select(
        "notes",
        columns="*",
        filters={"video_id": video_id},
        limit=1
    )
    
    notes_details = None
    if notes:
        notes_data = notes[0]
        notes_details = NotesDetails(
            summary=notes_data.get("summary"),
            keywords=notes_data.get("keywords", []),
            chapters=notes_data.get("chapters", []),
            insights=notes_data.get("insights", []),
            steps=notes_data.get("steps", []),
            quotes=notes_data.get("quotes", []),
            entities=notes_data.get("entities", {}),
        )
    
    # Get transcript preview (first 10 chunks)
    chunks = await supabase.select(
        "transcript_chunks",
        columns="start_ms,end_ms,text",
        filters={"video_id": video_id},
        order="start_ms.asc",
        limit=10
    )
    
    transcript_preview = [
        TranscriptChunk(
            start_ms=chunk["start_ms"],
            end_ms=chunk["end_ms"],
            text=chunk["text"]
        )
        for chunk in chunks
    ]
    
    return ItemResponse(
        video=VideoDetails(
            id=video_data["id"],
            title=video_data.get("title"),
            platform=video_data["platform"],
            duration_seconds=video_data.get("duration_seconds"),
            source_url=video_data["source_url"],
            storage_url=storage_url,
            created_at=video_data["created_at"],
            status=video_data["status"],
        ),
        notes=notes_details,
        transcript_preview=transcript_preview,
        status=video_data["status"],
    )
