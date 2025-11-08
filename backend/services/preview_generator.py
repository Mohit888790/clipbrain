"""Preview clip generation service using ffmpeg."""

import asyncio
from pathlib import Path


class PreviewGenerator:
    """Service for generating preview clips using ffmpeg."""
    
    @staticmethod
    async def generate_preview(
        input_file: Path,
        output_file: Path,
        start_seconds: float,
        duration_seconds: float = 12.0
    ) -> bool:
        """
        Generate a preview clip from media file.
        
        Args:
            input_file: Path to input media file
            output_file: Path to output preview file
            start_seconds: Start time in seconds
            duration_seconds: Duration of clip in seconds
        
        Returns:
            True if successful
        """
        cmd = [
            "ffmpeg",
            "-ss", str(start_seconds),
            "-t", str(duration_seconds),
            "-i", str(input_file),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-movflags", "+faststart",
            "-y",  # Overwrite output file
            str(output_file)
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            return process.returncode == 0 and output_file.exists()
        except Exception:
            return False


# Global preview generator instance
preview_generator = PreviewGenerator()
