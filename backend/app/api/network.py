from fastapi import APIRouter
from app.services import demo_data

router = APIRouter()

@router.get("/{mentee_id}")
async def get_network_data(mentee_id: str):
    """
    Get network graph data for visualization
    Returns nodes and edges for the mentee's network
    """
    network = demo_data.get_network_data()
    return {
        "mentee_id": mentee_id,
        **network
    }

@router.get("/{mentee_id}/stats")
async def get_network_stats(mentee_id: str):
    """
    Get network statistics
    """
    mentors = demo_data.get_demo_mentors()
    mentee = demo_data.get_demo_mentee()
    
    connected_mentors = [m for m in mentors if m["chat_history"] > 0]
    
    return {
        "mentee_id": mentee_id,
        "total_mentors": len(mentors),
        "connected_mentors": len(connected_mentors),
        "total_coffee_chats": sum(m["chat_history"] for m in mentors),
        "avg_match_score": sum(m["match_score"] for m in mentors) / len(mentors),
        "top_interests": mentee["interests"],
        "most_connected_field": "회계/재무",
    }