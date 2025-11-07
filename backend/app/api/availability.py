# backend/app/api/availability.py
# (수정) create_availability_slot에서 .select('*') 제거

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.core.config import supabase
from datetime import datetime, timezone
import uuid
from .auth import get_current_user_id 
from fastapi import Depends
router = APIRouter()

class AvailabilitySlot(BaseModel):
    mentor_id: uuid.UUID
    start_time: datetime
    end_time: datetime

@router.post("/api/availability/")
def create_availability_slot(slot: AvailabilitySlot):
    """
    멘토가 "커피챗 가능한 시간" 1개를 DB에 등록합니다.
    """
    try:
        response = supabase.table('mentor_availability').insert({
            "mentor_id": str(slot.mentor_id),
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "is_booked": False
        }).execute() # 👈 (수정) .select('*') 제거
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create availability slot")
            
        return response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/availability/{slot_id}")
def delete_availability_slot(
    slot_id: str, # (이전 수정사항) int -> str
    current_user_id: str = Depends(get_current_user_id) 
):
    # ... (기존 코드와 동일) ...
    try:
        response = supabase.table('mentor_availability') \
                           .delete() \
                           .eq('id', slot_id) \
                           .eq('mentor_id', current_user_id) \
                           .execute()
        
        if response.count == 0:
            raise HTTPException(status_code=404, detail="Slot not found or you do not have permission to delete it")
        
        return {"message": f"Slot {slot_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    cd
@router.get("/api/availability/{mentor_id}")
def get_mentor_availability(mentor_id: uuid.UUID):
    """
    특정 멘토의 '예약 가능한(is_booked=False)' 미래 시점의 슬롯 목록을 반환합니다.
    """
    try:
        # 1. ⭐️ 현재 UTC 시간을 ISO 포맷 문자열로 명확하게 정의합니다.
        current_utc_time = datetime.now(timezone.utc).isoformat()

        response = supabase.table('mentor_availability') \
                           .select("id, start_time, end_time") \
                           .eq('mentor_id', str(mentor_id)) \
                           .eq('is_booked', False) \
                           .gte('start_time', current_utc_time) \
                           .order('start_time', desc=False) \
                           .execute()
        
        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))