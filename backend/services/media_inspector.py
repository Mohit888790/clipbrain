"""Media inspection service using ffprobe."""

import asyncio
import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class MediaInfo:
    """Media file information."""
    duration_seconds: int | None = None
    audio_codec: str | None = None
    container_format: str | None = None
    language: str | None = None
    bitrate: int | None = None


class MediaInspector:
    """Service for inspecting media files using ffprobe."""
    
    @staticmethod
    async def inspect(file_path: Path) -> MediaInfo:
        """
        Inspect media file and extract metadata.
        
        Args:
            file_path: Path to media file
        
        Returns:
            MediaInfo with extracted metadata
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                
                # Extract format info
                format_info = data.get("format", {})
                duration = format_info.get("duration")
                container_format = format_info.get("format_name")
                bitrate = format_info.get("bit_rate")
                
                # Extract audio stream info
                audio_codec = None
                language = None
                
                for stream in data.get("streams", []):
                    if stream.get("codec_type") == "audio":
                        audio_codec = stream.get("codec_name")
                        language = stream.get("tags", {}).get("language")
                        break
                
                return MediaInfo(
                    duration_seconds=int(float(duration)) if duration else None,
                    audio_codec=audio_codec,
                    container_format=container_format,
                    language=language,
                    bitrate=int(bitrate) if bitrate else None,
                )
            else:
                return MediaInfo()
        
        except Exception:
            return MediaInfo()
