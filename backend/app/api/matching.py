from fastapi import APIRouter, Query
from typing import Optional
from app.services import demo_data

router = APIRouter()

@router.get("/calculate")
async def calculate_match_score(
    mentee_id: str = Query(...),
    mentor_id: str = Query(...),
):
    """
    Calculate detailed match score between mentee and mentor
    """
    mentor = demo_data.get_demo_mentor(mentor_id)
    mentee = demo_data.get_demo_mentee()
    
    if not mentor:
        return {"error": "Mentor not found"}, 404
    
    # Return detailed breakdown
    return {
        "mentee_id": mentee_id,
        "mentor_id": mentor_id,
        "similarity_score": mentor["match_score"] / 100.0,
        "distance_score": 1.0 / (1.0 + mentor["distance"] / 10.0),
        "final_score": mentor["match_score"],
        "distance_km": mentor["distance"],
        "common_interests": [
            tag for tag in mentor["tags"]
            if tag in mentee["interests"]
        ],
        "breakdown": {
            "career_similarity": 0.85,
            "field_match": 0.95,
            "experience_level": 0.90,
            "location_proximity": 0.80,
        }
    }

@router.post("/feedback")
async def submit_matching_feedback(
    mentee_id: str,
    mentor_id: str,
    rating: int,
    comment: Optional[str] = None
):
    """
    Submit feedback on matching quality
    This helps improve the AI algorithm
    """
    return {
        "success": True,
        "message": "Feedback received",
        "mentee_id": mentee_id,
        "mentor_id": mentor_id,
        "rating": rating,
    }