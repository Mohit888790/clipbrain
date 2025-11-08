"""Media downloader service using yt-dlp."""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Literal
from dataclasses import dataclass

ErrorCode = Literal[
    "RESTRICTED_CONTENT_UNSUPPORTED",
    "NOT_FOUND_OR_REMOVED",
    "PLATFORM_BLOCKED_TEMPORARILY",
    "UNSUPPORTED_PLATFORM",
    "DOWNLOAD_FAILED",
]


@dataclass
class DownloadResult:
    """Result of a download operation."""
    success: bool
    file_path: Path | None = None
    title: str | None = None
    duration_seconds: int | None = None
    language: str | None = None
    error_code: ErrorCode | None = None
    error_message: str | None = None


class MediaDownloader:
    """Service for downloading media using yt-dlp."""
    
    def __init__(self, download_dir: Path | None = None):
        """
        Initialize downloader.
        
        Args:
            download_dir: Directory to save downloads (default: ./downloads)
        """
        self.download_dir = download_dir or Path("./downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    async def download(self, url: str, video_id: str) -> DownloadResult:
        """
        Download media from URL.
        
        Args:
            url: Video URL
            video_id: UUID for the video
        
        Returns:
            DownloadResult with file path and metadata
        """
        output_template = str(self.download_dir / f"{video_id}.%(ext)s")
        
        # yt-dlp command
        cmd = [
            "yt-dlp",
            "-f", "bestaudio[ext=m4a]/bestaudio/best",
            "--no-playlist",
            "--no-warnings",
            "--retries", "2",
            "--socket-timeout", "30",
            "-o", output_template,
            "--print-json",
            "--no-simulate",
            url
        ]
        
        try:
            # Run yt-dlp
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse JSON output
                try:
                    info = json.loads(stdout.decode())
                    
                    # Find downloaded file
                    file_path = None
                    for ext in [".m4a", ".mp3", ".webm", ".mp4"]:
                        potential_path = self.download_dir / f"{video_id}{ext}"
                        if potential_path.exists():
                            file_path = potential_path
                            break
                    
                    if not file_path:
                        return DownloadResult(
                            success=False,
                            error_code="DOWNLOAD_FAILED",
                            error_message="Downloaded file not found"
                        )
                    
                    return DownloadResult(
                        success=True,
                        file_path=file_path,
                        title=info.get("title"),
                        duration_seconds=info.get("duration"),
                        language=info.get("language"),
                    )
                except json.JSONDecodeError:
                    # Fallback: find file manually
                    for ext in [".m4a", ".mp3", ".webm", ".mp4"]:
                        potential_path = self.download_dir / f"{video_id}{ext}"
                        if potential_path.exists():
                            return DownloadResult(
                                success=True,
                                file_path=potential_path,
                            )
                    
                    return DownloadResult(
                        success=False,
                        error_code="DOWNLOAD_FAILED",
                        error_message="Could not parse yt-dlp output"
                    )
            else:
                # Download failed, classify error
                error_output = stderr.decode().lower()
                error_code = self._classify_error(error_output)
                
                return DownloadResult(
                    success=False,
                    error_code=error_code,
                    error_message=stderr.decode()[:500]  # Truncate
                )
        
        except Exception as e:
            return DownloadResult(
                success=False,
                error_code="DOWNLOAD_FAILED",
                error_message=str(e)
            )
    
    def _classify_error(self, error_output: str) -> ErrorCode:
        """
        Classify error from yt-dlp output.
        
        Args:
            error_output: stderr from yt-dlp
        
        Returns:
            Error code
        """
        error_lower = error_output.lower()
        
        # Private/restricted content
        if any(keyword in error_lower for keyword in [
            "private video",
            "members-only",
            "this video is private",
            "login required",
            "sign in to confirm",
            "age-restricted",
        ]):
            return "RESTRICTED_CONTENT_UNSUPPORTED"
        
        # Not found or removed
        if any(keyword in error_lower for keyword in [
            "video unavailable",
            "video not found",
            "has been removed",
            "deleted",
            "404",
            "this video isn't available",
        ]):
            return "NOT_FOUND_OR_REMOVED"
        
        # Platform blocking
        if any(keyword in error_lower for keyword in [
            "429",
            "too many requests",
            "rate limit",
            "temporarily blocked",
            "try again later",
        ]):
            return "PLATFORM_BLOCKED_TEMPORARILY"
        
        # Unsupported platform
        if any(keyword in error_lower for keyword in [
            "unsupported url",
            "no suitable extractor",
        ]):
            return "UNSUPPORTED_PLATFORM"
        
        # Generic failure
        return "DOWNLOAD_FAILED"
    
    def cleanup(self, file_path: Path) -> None:
        """
        Delete downloaded file.
        
        Args:
            file_path: Path to file to delete
        """
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass
