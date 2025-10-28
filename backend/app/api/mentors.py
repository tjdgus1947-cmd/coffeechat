from fastapi import APIRouter, Query
from typing import List, Optional
from app.services import demo_data

router = APIRouter()

@router.get("/")
async def get_mentors(
    limit: int = Query(10, ge=1, le=100),
    tags: Optional[List[str]] = Query(None),
    max_distance: Optional[float] = Query(None),
    query: Optional[str] = Query(None),
):
    """
    Get list of mentors with optional filters
    """
    mentors = demo_data.search_mentors(
        query=query or "",
        tags=tags,
        max_distance=max_distance
    )
    return {
        "mentors": mentors[:limit],
        "total": len(mentors),
    }

@router.get("/{mentor_id}")
async def get_mentor(mentor_id: str):
    """
    Get specific mentor details
    """
    mentor = demo_data.get_demo_mentor(mentor_id)
    if not mentor:
        return {"error": "Mentor not found"}, 404
    return mentor

@router.get("/recommended/{mentee_id}")
async def get_recommended_mentors(
    mentee_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get AI-recommended mentors for a mentee
    Based on embeddings similarity + distance
    """
    mentors = demo_data.get_recommended_mentors(limit=limit)
    return {
        "mentee_id": mentee_id,
        "mentors": mentors,
        "total": len(mentors),
        "algorithm": "cosine_similarity + distance_score",
    }