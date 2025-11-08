"""Export routes."""

import io
import zipfile
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from supabase_client import supabase

router = APIRouter()


@router.get("/export")
async def export_data():
    """
    Export all data as ZIP file.
    
    Returns:
        ZIP file with JSON data and media files
    """
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Export videos
        videos = await supabase.select("videos", columns="*")
        zip_file.writestr("videos.json", json.dumps(videos, indent=2, default=str))
        
        # Export transcripts
        transcripts = await supabase.select("transcripts", columns="*")
        zip_file.writestr("transcripts.json", json.dumps(transcripts, indent=2, default=str))
        
        # Export transcript chunks (without embeddings to reduce size)
        chunks = await supabase.select(
            "transcript_chunks",
            columns="id,video_id,start_ms,end_ms,text,text_hash"
        )
        zip_file.writestr("transcript_chunks.json", json.dumps(chunks, indent=2, default=str))
        
        # Export notes
        notes = await supabase.select("notes", columns="*")
        zip_file.writestr("notes.json", json.dumps(notes, indent=2, default=str))
        
        # Export collections
        collections = await supabase.select("collections", columns="*")
        zip_file.writestr("collections.json", json.dumps(collections, indent=2, default=str))
        
        # Export collection items
        collection_items = await supabase.select("collection_items", columns="*")
        zip_file.writestr("collection_items.json", json.dumps(collection_items, indent=2, default=str))
        
        # Note: Media files are not included to keep ZIP size manageable
        # Users can download media files separately using signed URLs
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=clipbrain_export.zip"}
    )
