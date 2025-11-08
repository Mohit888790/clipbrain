"""Video processing pipeline."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase_client import supabase
from storage import storage_service
from services.downloader import MediaDownloader
from services.media_inspector import MediaInspector
from services.transcription import transcription_service
from services.chunker import chunker
from services.ai_service import ai_service


async def process_video_async(video_id: str, source_url: str):
    """
    Process video through the complete pipeline.
    
    Args:
        video_id: UUID of the video
        source_url: Source URL of the video
    """
    downloader = MediaDownloader()
    
    try:
        # Stage 1: Download media
        await supabase.update(
            "videos",
            {"status": "processing", "current_stage": "download"},
            {"id": video_id}
        )
        
        download_result = await downloader.download(source_url, video_id)
        
        if not download_result.success:
            await supabase.update(
                "videos",
                {
                    "status": "failed",
                    "fail_reason": download_result.error_code,
                    "current_stage": None
                },
                {"id": video_id}
            )
            return
        
        # Update video metadata
        update_data = {}
        if download_result.title:
            update_data["title"] = download_result.title
        if download_result.duration_seconds:
            update_data["duration_seconds"] = download_result.duration_seconds
        if download_result.language:
            update_data["language"] = download_result.language
        
        if update_data:
            await supabase.update("videos", update_data, {"id": video_id})
        
        # Inspect media file
        media_info = await MediaInspector.inspect(download_result.file_path)
        if media_info.duration_seconds and not download_result.duration_seconds:
            await supabase.update(
                "videos",
                {"duration_seconds": media_info.duration_seconds},
                {"id": video_id}
            )
            download_result.duration_seconds = media_info.duration_seconds
        
        # Stage 2: Upload to storage
        await supabase.update(
            "videos",
            {"current_stage": "upload"},
            {"id": video_id}
        )
        
        storage_path = await storage_service.upload_media(
            video_id,
            download_result.file_path,
            content_type="audio/mp4"
        )
        
        await supabase.update(
            "videos",
            {"storage_path": storage_path},
            {"id": video_id}
        )
        
        # Generate signed URL for transcription
        signed_url = await storage_service.generate_signed_url(storage_path, ttl=3600)
        
        # Clean up local file
        downloader.cleanup(download_result.file_path)
        
        # Stage 3: Transcribe
        await supabase.update(
            "videos",
            {"current_stage": "transcribe"},
            {"id": video_id}
        )
        
        transcript_result = await transcription_service.transcribe(signed_url)
        
        if not transcript_result.success:
            await supabase.update(
                "videos",
                {
                    "status": "failed",
                    "fail_reason": "TRANSCRIPTION_FAILED",
                    "current_stage": None
                },
                {"id": video_id}
            )
            return
        
        # Store full transcript
        await supabase.insert("transcripts", {
            "video_id": video_id,
            "full_text": transcript_result.full_text
        })
        
        # Stage 4: Generate notes
        await supabase.update(
            "videos",
            {"current_stage": "notes"},
            {"id": video_id}
        )
        
        notes_result = await ai_service.generate_notes(
            transcript_result.full_text,
            download_result.duration_seconds or 0
        )
        
        # Store notes (even if partial)
        notes_data = {
            "video_id": video_id,
            "summary": notes_result.summary,
            "keywords": notes_result.keywords or [],
            "chapters": notes_result.chapters or [],
            "insights": notes_result.insights or [],
            "steps": notes_result.steps or [],
            "quotes": notes_result.quotes or [],
            "entities": notes_result.entities or {},
        }
        
        if notes_result.raw_text:
            notes_data["notes_raw_text"] = notes_result.raw_text
        
        await supabase.insert("notes", notes_data)
        
        # Stage 5: Chunk transcript and generate embeddings
        await supabase.update(
            "videos",
            {"current_stage": "embeddings"},
            {"id": video_id}
        )
        
        # Chunk transcript
        chunks = chunker.chunk_transcript(transcript_result.word_timestamps)
        
        # Check for cached embeddings and generate new ones
        for chunk in chunks:
            # Check if embedding exists for this text_hash
            existing = await supabase.select(
                "transcript_chunks",
                columns="embedding",
                filters={"text_hash": chunk.text_hash},
                limit=1
            )
            
            embedding = None
            if existing and existing[0].get("embedding"):
                # Use cached embedding
                embedding = existing[0]["embedding"]
            else:
                # Generate new embedding
                embedding = await ai_service.generate_embedding(chunk.text)
            
            # Store chunk
            await supabase.insert("transcript_chunks", {
                "video_id": video_id,
                "start_ms": chunk.start_ms,
                "end_ms": chunk.end_ms,
                "text": chunk.text,
                "text_hash": chunk.text_hash,
                "embedding": embedding
            })
            
            # Rate limiting
            await asyncio.sleep(1.0)
        
        # Stage 6: Generate previews (optional - skip for now)
        # This can be implemented later or made async
        
        # Mark as done
        await supabase.update(
            "videos",
            {
                "status": "done",
                "current_stage": None
            },
            {"id": video_id}
        )
        
    except Exception as e:
        # Handle unexpected errors
        await supabase.update(
            "videos",
            {
                "status": "failed",
                "fail_reason": "DOWNLOAD_FAILED",
                "current_stage": None
            },
            {"id": video_id}
        )
        raise e


def process_video(video_id: str, source_url: str):
    """
    Synchronous wrapper for async pipeline.
    
    This is the function that RQ will call.
    
    Args:
        video_id: UUID of the video
        source_url: Source URL of the video
    """
    asyncio.run(process_video_async(video_id, source_url))
