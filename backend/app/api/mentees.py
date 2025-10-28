from fastapi import APIRouter
from app.services import demo_data

router = APIRouter()

@router.get("/{mentee_id}")
async def get_mentee(mentee_id: str):
    """
    Get mentee profile
    """
    mentee = demo_data.get_demo_mentee()
    return mentee

@router.get("/{mentee_id}/history")
async def get_mentee_history(mentee_id: str):
    """
    Get mentee's coffee chat history
    """
    # Return mentors with chat_history > 0
    all_mentors = demo_data.get_demo_mentors()
    history = [m for m in all_mentors if m["chat_history"] > 0]
    
    return {
        "mentee_id": mentee_id,
        "total_chats": sum(m["chat_history"] for m in history),
        "unique_mentors": len(history),
        "history": history,
    }