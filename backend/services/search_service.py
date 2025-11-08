"""Search service with hybrid ranking."""

import asyncio
from dataclasses import dataclass
from supabase_client import supabase
from services.ai_service import ai_service
from storage import storage_service


@dataclass
class SearchResult:
    """Single search result."""
    video_id: str
    title: str | None
    platform: str
    start_ms: int
    end_ms: int
    snippet: str
    score: float
    tags: list[str]
    chapter_title: str | None
    source_url: str
    deep_link: str | None
    preview_url: str | None


class SearchService:
    """Service for hybrid search combining vector and full-text search."""
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 20,
        tags: list[str] | None = None,
        platform: str | None = None
    ) -> list[SearchResult]:
        """
        Perform hybrid search combining vector similarity and full-text search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            tags: Filter by tags
            platform: Filter by platform
        
        Returns:
            List of search results sorted by score
        """
        # Generate query embedding
        query_embedding = await ai_service.generate_embedding(query)
        
        # Run both searches in parallel
        vector_results, text_results = await asyncio.gather(
            self.vector_search(query_embedding, top_k=50) if query_embedding else asyncio.sleep(0, result=[]),
            self.fulltext_search(query, top_k=50)
        )
        
        # Merge and rank results
        merged_results = self.merge_results(
            vector_results,
            text_results,
            tags=tags,
            platform=platform
        )
        
        # Group by video and keep top spans
        grouped_results = self._group_by_video(merged_results, max_per_video=3)
        
        # Sort by score and limit
        grouped_results.sort(key=lambda x: x.score, reverse=True)
        
        # Decorate with metadata
        decorated_results = await self._decorate_results(grouped_results[:top_k])
        
        return decorated_results
    
    async def vector_search(
        self,
        query_embedding: list[float],
        top_k: int = 50
    ) -> list[dict]:
        """
        Perform vector similarity search.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
        
        Returns:
            List of results with similarity scores
        """
        # Use Supabase RPC for vector search
        # Note: This requires a custom PostgreSQL function
        # For now, we'll use a simplified approach
        
        # Get all chunks (in production, use pgvector KNN)
        chunks = await supabase.select(
            "transcript_chunks",
            columns="id,video_id,start_ms,end_ms,text,embedding"
        )
        
        # Calculate cosine similarity
        results = []
        for chunk in chunks:
            if chunk.get("embedding"):
                similarity = self._cosine_similarity(
                    query_embedding,
                    chunk["embedding"]
                )
                results.append({
                    "video_id": chunk["video_id"],
                    "start_ms": chunk["start_ms"],
                    "end_ms": chunk["end_ms"],
                    "text": chunk["text"],
                    "score": similarity,
                    "source": "vector"
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    async def fulltext_search(
        self,
        query: str,
        top_k: int = 50
    ) -> list[dict]:
        """
        Perform full-text search.
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of results with relevance scores
        """
        # Search in transcripts
        # Note: This is simplified; production should use PostgreSQL full-text search
        
        transcripts = await supabase.select(
            "transcripts",
            columns="video_id,full_text"
        )
        
        results = []
        query_lower = query.lower()
        
        for transcript in transcripts:
            full_text = transcript.get("full_text", "")
            full_text_lower = full_text.lower()
            
            # Simple keyword matching
            if query_lower in full_text_lower:
                # Find position
                pos = full_text_lower.find(query_lower)
                
                # Extract snippet
                snippet_start = max(0, pos - 100)
                snippet_end = min(len(full_text), pos + 100)
                snippet = full_text[snippet_start:snippet_end]
                
                # Calculate simple relevance score
                count = full_text_lower.count(query_lower)
                score = min(1.0, count / 10.0)
                
                results.append({
                    "video_id": transcript["video_id"],
                    "start_ms": 0,
                    "end_ms": 0,
                    "text": snippet,
                    "score": score,
                    "source": "text"
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def merge_results(
        self,
        vector_results: list[dict],
        text_results: list[dict],
        tags: list[str] | None = None,
        platform: str | None = None
    ) -> list[dict]:
        """
        Merge and rank results from vector and text search.
        
        Args:
            vector_results: Results from vector search
            text_results: Results from full-text search
            tags: Filter by tags
            platform: Filter by platform
        
        Returns:
            Merged and ranked results
        """
        # Normalize scores to [0, 1]
        vector_results = self._normalize_scores(vector_results)
        text_results = self._normalize_scores(text_results)
        
        # Combine results
        combined = {}
        
        # Add vector results with weight 0.6
        for result in vector_results:
            key = f"{result['video_id']}_{result['start_ms']}"
            combined[key] = {
                **result,
                "final_score": result["score"] * 0.6
            }
        
        # Add text results with weight 0.4
        for result in text_results:
            key = f"{result['video_id']}_{result['start_ms']}"
            if key in combined:
                combined[key]["final_score"] += result["score"] * 0.4
            else:
                combined[key] = {
                    **result,
                    "final_score": result["score"] * 0.4
                }
        
        return list(combined.values())
    
    def _group_by_video(
        self,
        results: list[dict],
        max_per_video: int = 3
    ) -> list[dict]:
        """Group results by video and keep top spans per video."""
        grouped = {}
        
        for result in results:
            video_id = result["video_id"]
            if video_id not in grouped:
                grouped[video_id] = []
            grouped[video_id].append(result)
        
        # Keep top spans per video
        final_results = []
        for video_id, video_results in grouped.items():
            video_results.sort(key=lambda x: x["final_score"], reverse=True)
            final_results.extend(video_results[:max_per_video])
        
        return final_results
    
    async def _decorate_results(
        self,
        results: list[dict]
    ) -> list[SearchResult]:
        """Decorate results with metadata."""
        # Get video metadata
        video_ids = list(set(r["video_id"] for r in results))
        
        videos_data = {}
        notes_data = {}
        
        for video_id in video_ids:
            video = await supabase.select(
                "videos",
                columns="id,title,platform,source_url,storage_path",
                filters={"id": video_id},
                limit=1
            )
            if video:
                videos_data[video_id] = video[0]
            
            notes = await supabase.select(
                "notes",
                columns="keywords,chapters",
                filters={"video_id": video_id},
                limit=1
            )
            if notes:
                notes_data[video_id] = notes[0]
        
        # Decorate results
        decorated = []
        for result in results:
            video_id = result["video_id"]
            video = videos_data.get(video_id, {})
            notes = notes_data.get(video_id, {})
            
            # Generate deep link
            deep_link = self._generate_deep_link(
                video.get("source_url", ""),
                video.get("platform", ""),
                result["start_ms"]
            )
            
            # Generate signed URL for preview
            preview_url = None
            if video.get("storage_path"):
                try:
                    preview_url = await storage_service.generate_signed_url(
                        video["storage_path"]
                    )
                except Exception:
                    pass
            
            # Find chapter title
            chapter_title = self._find_chapter(
                notes.get("chapters", []),
                result["start_ms"]
            )
            
            decorated.append(SearchResult(
                video_id=video_id,
                title=video.get("title"),
                platform=video.get("platform", ""),
                start_ms=result["start_ms"],
                end_ms=result["end_ms"],
                snippet=result["text"],
                score=result["final_score"],
                tags=notes.get("keywords", []),
                chapter_title=chapter_title,
                source_url=video.get("source_url", ""),
                deep_link=deep_link,
                preview_url=preview_url,
            ))
        
        return decorated
    
    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = sum(x * x for x in a) ** 0.5
        magnitude_b = sum(x * x for x in b) ** 0.5
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)
    
    @staticmethod
    def _normalize_scores(results: list[dict]) -> list[dict]:
        """Normalize scores to [0, 1] range."""
        if not results:
            return results
        
        scores = [r["score"] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            for r in results:
                r["score"] = 1.0
        else:
            for r in results:
                r["score"] = (r["score"] - min_score) / (max_score - min_score)
        
        return results
    
    @staticmethod
    def _generate_deep_link(
        source_url: str,
        platform: str,
        start_ms: int
    ) -> str | None:
        """Generate deep link with timestamp."""
        start_seconds = int(start_ms / 1000)
        
        if platform == "youtube":
            # Add timestamp parameter
            separator = "&" if "?" in source_url else "?"
            return f"{source_url}{separator}t={start_seconds}"
        else:
            # Instagram, TikTok, Facebook don't support timestamps
            return source_url
    
    @staticmethod
    def _find_chapter(chapters: list[dict], timestamp_ms: int) -> str | None:
        """Find chapter title for given timestamp."""
        if not chapters:
            return None
        
        # Sort chapters by start time
        sorted_chapters = sorted(chapters, key=lambda c: c.get("start_ms", 0))
        
        # Find the chapter that contains this timestamp
        current_chapter = None
        for chapter in sorted_chapters:
            if chapter.get("start_ms", 0) <= timestamp_ms:
                current_chapter = chapter.get("title")
            else:
                break
        
        return current_chapter


# Global search service instance
search_service = SearchService()
