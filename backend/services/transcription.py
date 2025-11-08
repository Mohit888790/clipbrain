"""Transcription service using Deepgram API."""

import asyncio
import httpx
from dataclasses import dataclass
from config import settings


@dataclass
class WordTimestamp:
    """Word-level timestamp."""
    word: str
    start_ms: int
    end_ms: int


@dataclass
class TranscriptResult:
    """Transcription result."""
    success: bool
    full_text: str | None = None
    word_timestamps: list[WordTimestamp] | None = None
    language: str | None = None
    error_message: str | None = None


class TranscriptionService:
    """Service for transcribing audio using Deepgram."""
    
    def __init__(self):
        self.api_key = settings.deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1/listen"
    
    async def transcribe(self, audio_url: str) -> TranscriptResult:
        """
        Transcribe audio from URL using Deepgram Enhanced Batch model.
        
        Args:
            audio_url: Signed URL to audio file
        
        Returns:
            TranscriptResult with full text and word timestamps
        """
        # Retry logic: 1 retry with 10-second delay
        for attempt in range(2):
            try:
                result = await self._transcribe_attempt(audio_url)
                if result.success:
                    return result
                
                # If first attempt failed, retry
                if attempt == 0:
                    await asyncio.sleep(10)
                else:
                    return result
            except Exception as e:
                if attempt == 0:
                    await asyncio.sleep(10)
                else:
                    return TranscriptResult(
                        success=False,
                        error_message=str(e)
                    )
        
        return TranscriptResult(success=False, error_message="Transcription failed")
    
    async def _transcribe_attempt(self, audio_url: str) -> TranscriptResult:
        """Single transcription attempt."""
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Request parameters
        params = {
            "model": "nova-2",
            "smart_format": "true",
            "punctuate": "true",
            "utterances": "true",
            "diarize": "false",
        }
        
        payload = {
            "url": audio_url
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                params=params,
                json=payload,
            )
            
            if response.status_code != 200:
                return TranscriptResult(
                    success=False,
                    error_message=f"Deepgram API error: {response.status_code}"
                )
            
            data = response.json()
            
            # Extract transcript
            results = data.get("results", {})
            channels = results.get("channels", [])
            
            if not channels:
                return TranscriptResult(
                    success=False,
                    error_message="No transcript data in response"
                )
            
            alternatives = channels[0].get("alternatives", [])
            if not alternatives:
                return TranscriptResult(
                    success=False,
                    error_message="No alternatives in response"
                )
            
            alternative = alternatives[0]
            full_text = alternative.get("transcript", "")
            
            # Extract word timestamps
            word_timestamps = []
            for word_data in alternative.get("words", []):
                word_timestamps.append(WordTimestamp(
                    word=word_data.get("word", ""),
                    start_ms=int(word_data.get("start", 0) * 1000),
                    end_ms=int(word_data.get("end", 0) * 1000),
                ))
            
            # Detect language
            language = results.get("channels", [{}])[0].get("detected_language")
            
            return TranscriptResult(
                success=True,
                full_text=full_text,
                word_timestamps=word_timestamps,
                language=language,
            )


# Global transcription service instance
transcription_service = TranscriptionService()
