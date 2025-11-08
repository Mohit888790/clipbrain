"""Supabase Storage client wrapper."""

import httpx
from pathlib import Path
from typing import BinaryIO

from config import settings


class StorageService:
    """Service for interacting with Supabase Storage."""
    
    def __init__(self):
        self.base_url = f"{settings.supabase_url}/storage/v1"
        self.bucket_name = "videos"
        self.headers = {
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "apikey": settings.supabase_service_key,
        }
    
    async def upload_media(
        self, 
        video_id: str, 
        file_path: Path,
        content_type: str = "audio/mp4"
    ) -> str:
        """
        Upload media file to Supabase Storage with retry logic.
        
        Args:
            video_id: UUID of the video
            file_path: Path to the file to upload
            content_type: MIME type of the file
        
        Returns:
            Storage path of the uploaded file
        """
        import asyncio
        
        storage_path = f"{video_id}/original{file_path.suffix}"
        url = f"{self.base_url}/object/{self.bucket_name}/{storage_path}"
        
        # Retry logic: 1 retry with 10-second delay
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    with open(file_path, "rb") as f:
                        response = await client.post(
                            url,
                            headers={
                                **self.headers,
                                "Content-Type": content_type,
                            },
                            content=f.read(),
                        )
                        response.raise_for_status()
                
                return storage_path
            except Exception as e:
                if attempt == 0:
                    # First attempt failed, wait and retry
                    await asyncio.sleep(10)
                else:
                    # Second attempt failed, raise
                    raise e
        
        return storage_path
    
    async def generate_signed_url(
        self, 
        storage_path: str, 
        ttl: int | None = None
    ) -> str:
        """
        Generate a signed URL for accessing a file.
        
        Args:
            storage_path: Path to the file in storage
            ttl: Time-to-live in seconds (default from settings)
        
        Returns:
            Signed URL
        """
        if ttl is None:
            ttl = settings.signed_url_ttl_seconds
        
        url = f"{self.base_url}/object/sign/{self.bucket_name}/{storage_path}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"expiresIn": ttl},
            )
            response.raise_for_status()
            data = response.json()
        
        # Construct full signed URL
        signed_path = data["signedURL"]
        return f"{settings.supabase_url}/storage/v1{signed_path}"
    
    async def upload_preview(
        self,
        video_id: str,
        clip_file: Path,
        start_ms: int,
        end_ms: int
    ) -> str:
        """
        Upload a preview clip to storage with retry logic.
        
        Args:
            video_id: UUID of the video
            clip_file: Path to the preview clip file
            start_ms: Start timestamp in milliseconds
            end_ms: End timestamp in milliseconds
        
        Returns:
            Storage path of the uploaded preview
        """
        import asyncio
        
        storage_path = f"{video_id}/previews/{start_ms}_{end_ms}.mp4"
        url = f"{self.base_url}/object/{self.bucket_name}/{storage_path}"
        
        # Retry logic: 1 retry with 10-second delay
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    with open(clip_file, "rb") as f:
                        response = await client.post(
                            url,
                            headers={
                                **self.headers,
                                "Content-Type": "video/mp4",
                            },
                            content=f.read(),
                        )
                        response.raise_for_status()
                
                return storage_path
            except Exception as e:
                if attempt == 0:
                    await asyncio.sleep(10)
                else:
                    raise e
        
        return storage_path
    
    async def delete_file(self, storage_path: str) -> None:
        """
        Delete a file from storage.
        
        Args:
            storage_path: Path to the file in storage
        """
        url = f"{self.base_url}/object/{self.bucket_name}/{storage_path}"
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers=self.headers,
            )
            response.raise_for_status()


# Global storage service instance
storage_service = StorageService()
