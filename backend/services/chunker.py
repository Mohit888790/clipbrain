"""Transcript chunking service."""

import hashlib
from dataclasses import dataclass
from services.transcription import WordTimestamp


@dataclass
class TranscriptChunk:
    """A chunk of transcript with timestamps."""
    start_ms: int
    end_ms: int
    text: str
    text_hash: str


class TranscriptChunker:
    """Service for chunking transcripts into time-based segments."""
    
    def __init__(
        self,
        chunk_duration_ms: int = 12500,  # 12.5 seconds
        overlap_ms: int = 1500,  # 1.5 seconds
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_duration_ms: Target chunk duration in milliseconds
            overlap_ms: Overlap between chunks in milliseconds
        """
        self.chunk_duration_ms = chunk_duration_ms
        self.overlap_ms = overlap_ms
    
    def chunk_transcript(
        self,
        word_timestamps: list[WordTimestamp]
    ) -> list[TranscriptChunk]:
        """
        Chunk transcript into time-based segments.
        
        Args:
            word_timestamps: List of words with timestamps
        
        Returns:
            List of transcript chunks
        """
        if not word_timestamps:
            return []
        
        chunks = []
        current_chunk_words = []
        chunk_start_ms = word_timestamps[0].start_ms
        
        for i, word in enumerate(word_timestamps):
            current_chunk_words.append(word)
            
            # Check if we should end this chunk
            chunk_duration = word.end_ms - chunk_start_ms
            is_last_word = i == len(word_timestamps) - 1
            
            should_end_chunk = (
                chunk_duration >= self.chunk_duration_ms or
                is_last_word
            )
            
            if should_end_chunk and current_chunk_words:
                # Create chunk
                chunk_text = " ".join(w.word for w in current_chunk_words)
                chunk_end_ms = current_chunk_words[-1].end_ms
                
                chunk = TranscriptChunk(
                    start_ms=chunk_start_ms,
                    end_ms=chunk_end_ms,
                    text=chunk_text,
                    text_hash=self._generate_text_hash(chunk_text),
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                if not is_last_word:
                    # Find words that fall within overlap period
                    overlap_start_ms = chunk_end_ms - self.overlap_ms
                    overlap_words = [
                        w for w in current_chunk_words
                        if w.start_ms >= overlap_start_ms
                    ]
                    
                    # Start next chunk
                    if overlap_words:
                        current_chunk_words = overlap_words
                        chunk_start_ms = overlap_words[0].start_ms
                    else:
                        # No overlap, start fresh
                        current_chunk_words = []
                        if i + 1 < len(word_timestamps):
                            chunk_start_ms = word_timestamps[i + 1].start_ms
        
        return chunks
    
    @staticmethod
    def _generate_text_hash(text: str) -> str:
        """
        Generate SHA-256 hash of normalized text.
        
        Args:
            text: Text to hash
        
        Returns:
            Hex digest of hash
        """
        # Normalize: lowercase, strip extra whitespace
        normalized = " ".join(text.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()


# Global chunker instance
chunker = TranscriptChunker()
