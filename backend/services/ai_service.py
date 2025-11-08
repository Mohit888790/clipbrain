"""AI service using Google Gemini API."""

import asyncio
import json
import httpx
from dataclasses import dataclass
from config import settings


@dataclass
class NotesResult:
    """AI-generated notes result."""
    success: bool
    summary: str | None = None
    keywords: list[str] | None = None
    chapters: list[dict] | None = None
    insights: list[str] | None = None
    steps: list[str] | None = None
    quotes: list[dict] | None = None
    entities: dict | None = None
    raw_text: str | None = None
    error_message: str | None = None


class AIService:
    """Service for AI operations using Gemini API."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.generation_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.embedding_url = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
    
    async def generate_notes(
        self,
        transcript: str,
        duration_seconds: int
    ) -> NotesResult:
        """
        Generate structured notes from transcript.
        
        Args:
            transcript: Full transcript text
            duration_seconds: Video duration in seconds
        
        Returns:
            NotesResult with structured notes
        """
        # Build prompt
        include_chapters = duration_seconds >= 300  # 5 minutes
        
        system_prompt = self._build_notes_prompt(include_chapters)
        
        # Retry logic: 1 retry with clarifier prompt
        for attempt in range(2):
            try:
                result = await self._generate_notes_attempt(
                    transcript,
                    system_prompt,
                    is_retry=attempt > 0
                )
                
                if result.success:
                    return result
                
                # First attempt failed, retry with clarifier
                if attempt == 0:
                    await asyncio.sleep(5)
            except Exception as e:
                if attempt == 0:
                    await asyncio.sleep(5)
                else:
                    return NotesResult(
                        success=False,
                        error_message=str(e)
                    )
        
        return NotesResult(success=False, error_message="Notes generation failed")
    
    def _build_notes_prompt(self, include_chapters: bool) -> str:
        """Build system prompt for notes generation."""
        chapters_field = """
  "chapters": [{"title": "string", "start_ms": number}],""" if include_chapters else ""
        
        return f"""Extract structured information from this video transcript.
Return ONLY valid JSON with this exact schema:
{{
  "summary": "string (8-10 lines max)",
  "keywords": ["string"] (12 max),{chapters_field}
  "insights": ["string"],
  "steps": ["string"],
  "quotes": [{{"text": "string", "start_ms": number}}],
  "entities": {{"people": [], "tools": [], "urls": []}}
}}

Rules:
- summary: Concise overview, 8-10 lines maximum
- keywords: Most important tags/topics, 12 maximum
- insights: Key takeaways or learnings
- steps: If tutorial/how-to, list steps in order
- quotes: Notable quotes with approximate timestamp in milliseconds
- entities: Extract people names, tools/technologies mentioned, and URLs
{"- chapters: Major sections with titles and start times (only for videos >= 5 minutes)" if include_chapters else ""}

Return ONLY the JSON object, no markdown formatting."""
    
    async def _generate_notes_attempt(
        self,
        transcript: str,
        system_prompt: str,
        is_retry: bool = False
    ) -> NotesResult:
        """Single notes generation attempt."""
        # Truncate transcript if too long (Gemini has token limits)
        max_chars = 30000
        truncated_transcript = transcript[:max_chars]
        if len(transcript) > max_chars:
            truncated_transcript += "\n\n[Transcript truncated...]"
        
        user_message = f"Transcript:\n\n{truncated_transcript}"
        
        if is_retry:
            user_message += "\n\nIMPORTANT: Return ONLY valid JSON, no markdown code blocks."
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_prompt}\n\n{user_message}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.generation_url}?key={self.api_key}",
                json=payload,
            )
            
            if response.status_code != 200:
                return NotesResult(
                    success=False,
                    error_message=f"Gemini API error: {response.status_code}"
                )
            
            data = response.json()
            
            # Extract generated text
            candidates = data.get("candidates", [])
            if not candidates:
                return NotesResult(
                    success=False,
                    error_message="No candidates in response"
                )
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                return NotesResult(
                    success=False,
                    error_message="No parts in response"
                )
            
            generated_text = parts[0].get("text", "")
            
            # Parse JSON
            try:
                # Remove markdown code blocks if present
                json_text = generated_text.strip()
                if json_text.startswith("```"):
                    # Extract JSON from code block
                    lines = json_text.split("\n")
                    json_text = "\n".join(lines[1:-1])
                
                notes_data = json.loads(json_text)
                
                return NotesResult(
                    success=True,
                    summary=notes_data.get("summary"),
                    keywords=notes_data.get("keywords", []),
                    chapters=notes_data.get("chapters", []),
                    insights=notes_data.get("insights", []),
                    steps=notes_data.get("steps", []),
                    quotes=notes_data.get("quotes", []),
                    entities=notes_data.get("entities", {}),
                )
            except json.JSONDecodeError:
                # JSON parsing failed, store raw text
                return NotesResult(
                    success=False,
                    raw_text=generated_text,
                    error_message="Failed to parse JSON response"
                )
    
    async def generate_embedding(self, text: str) -> list[float] | None:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None if failed
        """
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.embedding_url}?key={self.api_key}",
                    json=payload,
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                embedding = data.get("embedding", {}).get("values", [])
                return embedding if embedding else None
        except Exception:
            return None
    
    async def batch_embeddings(
        self,
        texts: list[str],
        rate_limit_delay: float = 1.0
    ) -> list[list[float] | None]:
        """
        Generate embeddings for multiple texts with rate limiting.
        
        Args:
            texts: List of texts to embed
            rate_limit_delay: Delay between requests in seconds
        
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
            
            # Rate limiting: wait between requests (except last one)
            if i < len(texts) - 1:
                await asyncio.sleep(rate_limit_delay)
        
        return embeddings


# Global AI service instance
ai_service = AIService()
