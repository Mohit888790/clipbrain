"""Collections management routes."""

from fastapi import APIRouter, HTTPException
from models import CreateCollectionRequest, CollectionDetails, CollectionWithVideos, VideoDetails
from supabase_client import supabase

router = APIRouter()


@router.post("/collections", response_model=CollectionDetails)
async def create_collection(request: CreateCollectionRequest):
    """
    Create a new collection.
    
    Args:
        request: Collection creation request
    
    Returns:
        Created collection details
    """
    try:
        created = await supabase.insert("collections", {"name": request.name})
        collection = created[0]
        
        return CollectionDetails(
            id=collection["id"],
            name=collection["name"],
            created_at=collection["created_at"],
        )
    except Exception as e:
        # Handle unique constraint violation
        if "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Collection name already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections/{collection_id}/items")
async def add_video_to_collection(collection_id: str, video_id: str):
    """
    Add video to collection.
    
    Args:
        collection_id: Collection ID
        video_id: Video ID (from query parameter)
    
    Returns:
        Success message
    """
    # Check collection exists
    collection = await supabase.select(
        "collections",
        columns="id",
        filters={"id": collection_id},
        limit=1
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Check video exists
    video = await supabase.select(
        "videos",
        columns="id",
        filters={"id": video_id},
        limit=1
    )
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Add to collection (ignore if already exists)
    try:
        await supabase.insert("collection_items", {
            "collection_id": collection_id,
            "video_id": video_id
        })
    except Exception:
        # Already exists, that's fine
        pass
    
    return {"message": "Video added to collection"}


@router.delete("/collections/{collection_id}/items/{video_id}")
async def remove_video_from_collection(collection_id: str, video_id: str):
    """
    Remove video from collection.
    
    Args:
        collection_id: Collection ID
        video_id: Video ID
    
    Returns:
        Success message
    """
    await supabase.delete(
        "collection_items",
        filters={
            "collection_id": collection_id,
            "video_id": video_id
        }
    )
    
    return {"message": "Video removed from collection"}


@router.get("/collections", response_model=list[CollectionDetails])
async def list_collections():
    """
    List all collections with video counts.
    
    Returns:
        List of collections
    """
    collections = await supabase.select("collections", columns="*")
    
    # Get video counts
    result = []
    for collection in collections:
        items = await supabase.select(
            "collection_items",
            columns="video_id",
            filters={"collection_id": collection["id"]}
        )
        
        result.append(CollectionDetails(
            id=collection["id"],
            name=collection["name"],
            created_at=collection["created_at"],
            video_count=len(items),
        ))
    
    return result


@router.get("/collections/{collection_id}", response_model=CollectionWithVideos)
async def get_collection(collection_id: str):
    """
    Get collection details with videos.
    
    Args:
        collection_id: Collection ID
    
    Returns:
        Collection with videos
    """
    # Get collection
    collection = await supabase.select(
        "collections",
        columns="*",
        filters={"id": collection_id},
        limit=1
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    collection_data = collection[0]
    
    # Get videos in collection
    items = await supabase.select(
        "collection_items",
        columns="video_id",
        filters={"collection_id": collection_id}
    )
    
    videos = []
    for item in items:
        video = await supabase.select(
            "videos",
            columns="*",
            filters={"id": item["video_id"]},
            limit=1
        )
        if video:
            video_data = video[0]
            videos.append(VideoDetails(
                id=video_data["id"],
                title=video_data.get("title"),
                platform=video_data["platform"],
                duration_seconds=video_data.get("duration_seconds"),
                source_url=video_data["source_url"],
                storage_url=None,  # Don't generate signed URLs for list
                created_at=video_data["created_at"],
                status=video_data["status"],
            ))
    
    return CollectionWithVideos(
        id=collection_data["id"],
        name=collection_data["name"],
        created_at=collection_data["created_at"],
        videos=videos,
    )
