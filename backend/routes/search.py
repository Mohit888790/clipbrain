"""Search routes."""

import time
from fastapi import APIRouter
from models import SearchRequest, SearchResponse, SearchResult as SearchResultModel
from services.search_service import search_service

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_videos(request: SearchRequest):
    """
    Search videos using hybrid search.
    
    Args:
        request: Search request with query and filters
    
    Returns:
        Search results with scores and metadata
    """
    start_time = time.time()
    
    # Perform search
    results = await search_service.hybrid_search(
        query=request.q,
        top_k=request.top_k,
        tags=request.tags,
        platform=request.platform,
    )
    
    # Convert to response models
    result_models = [
        SearchResultModel(
            video_id=r.video_id,
            title=r.title,
            platform=r.platform,
            start_ms=r.start_ms,
            end_ms=r.end_ms,
            snippet=r.snippet,
            score=r.score,
            tags=r.tags,
            chapter_title=r.chapter_title,
            source_url=r.source_url,
            deep_link=r.deep_link,
            preview_url=r.preview_url,
        )
        for r in results
    ]
    
    query_time_ms = (time.time() - start_time) * 1000
    
    return SearchResponse(
        results=result_models,
        total=len(result_models),
        query_time_ms=query_time_ms,
    )
