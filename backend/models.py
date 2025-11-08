"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from uuid import UUID


# Enums
Platform = Literal["youtube", "instagram", "tiktok", "facebook"]
VideoStatus = Literal["queued", "processing", "done", "failed"]
PipelineStage = Literal["download", "upload", "transcribe", "notes", "embeddings", "previews"]


# Request Models
class IngestRequest(BaseModel):
    """Request to ingest a video URL."""
    url: str = Field(..., description="Video URL from supported platform")


class SearchRequest(BaseModel):
    """Request to search videos."""
    q: str = Field(..., description="Search query")
    top_k: int = Field(20, ge=1, le=100, description="Number of results to return")
    tags: list[str] | None = Field(None, description="Filter by tags")
    platform: Platform | None = Field(None, description="Filter by platform")


class UpdateTagsRequest(BaseModel):
    """Request to update video tags."""
    keywords: list[str] = Field(..., description="List of keywords/tags")


class CreateCollectionRequest(BaseModel):
    """Request to create a collection."""
    name: str = Field(..., min_length=1, max_length=100, description="Collection name")


# Response Models
class IngestResponse(BaseModel):
    """Response from ingesting a video."""
    job_id: str
    video_id: str


class JobStatusResponse(BaseModel):
    """Response for job status."""
    status: VideoStatus
    video_id: str
    fail_reason: str | None = None
    current_stage: PipelineStage | None = None


class VideoDetails(BaseModel):
    """Video metadata."""
    id: str
    title: str | None
    platform: Platform
    duration_seconds: int | None
    source_url: str
    storage_url: str | None
    created_at: datetime
    status: VideoStatus


class NotesDetails(BaseModel):
    """AI-generated notes."""
    summary: str | None
    keywords: list[str]
    chapters: list[dict]
    insights: list[str]
    steps: list[str]
    quotes: list[dict]
    entities: dict


class TranscriptChunk(BaseModel):
    """Transcript chunk with timestamp."""
    start_ms: int
    end_ms: int
    text: str


class ItemResponse(BaseModel):
    """Response for video item details."""
    video: VideoDetails
    notes: NotesDetails | None
    transcript_preview: list[TranscriptChunk]
    status: VideoStatus


class SearchResult(BaseModel):
    """Single search result."""
    video_id: str
    title: str | None
    platform: Platform
    start_ms: int
    end_ms: int
    snippet: str
    score: float
    tags: list[str]
    chapter_title: str | None = None
    source_url: str
    deep_link: str | None = None
    preview_url: str | None = None


class SearchResponse(BaseModel):
    """Response from search."""
    results: list[SearchResult]
    total: int
    query_time_ms: float


class JumpResponse(BaseModel):
    """Response for jump/deep link."""
    deep_link: str
    signed_play_url: str
    start_seconds: float


class CollectionDetails(BaseModel):
    """Collection metadata."""
    id: str
    name: str
    created_at: datetime
    video_count: int | None = None


class CollectionWithVideos(BaseModel):
    """Collection with its videos."""
    id: str
    name: str
    created_at: datetime
    videos: list[VideoDetails]


class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "unhealthy"]
    redis: bool
    supabase: bool
    timestamp: datetime
