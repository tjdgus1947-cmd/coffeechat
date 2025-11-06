# File: tjdgus1947-cmd/coffeechat/coffeechat-db-ksh/backend/app/api/availability.py

from fastapi import APIRouter, HTTPException, Body, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.config import supabase
import uuid
# jsonable_encoder 임포트 추가
from fastapi.encoders import jsonable_encoder 

router = APIRouter()

# --- 스키마 정의 ---
class AvailabilitySlot(BaseModel):
    mentor_id: uuid.UUID
    start_time: datetime
    end_time: datetime

class AvailabilityUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# --- 1. 생성 (POST) API ---
@router.post("/api/availability/")
def create_availability_slot(slot: AvailabilitySlot):
    try:
        response = supabase.table('mentor_availability').insert({
            "mentor_id": str(slot.mentor_id),
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "is_booked": False
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve inserted data")
            
        return jsonable_encoder(response.data[0])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- 2. 조회 (GET) API ---
@router.get("/api/availability/{mentor_id}")
def get_mentor_availability(mentor_id: uuid.UUID):
    try:
        response = supabase.table('mentor_availability') \
                           .select("*") \
                           .eq('mentor_id', str(mentor_id)) \
                           .eq('is_booked', False) \
                           .gte('start_time', datetime.now().isoformat()) \
                           .order('start_time', desc=False) \
                           .execute()
        
        return jsonable_encoder(response.data)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# --- 3. 수정 (PUT) API ---
@router.put("/api/availability/{slot_id}") 
def update_availability_slot(slot_id: uuid.UUID, update_data: AvailabilityUpdate):
    try:
        update_payload = update_data.model_dump(exclude_none=True)
        
        if not update_payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
            
        response = supabase.table('mentor_availability') \
                           .update(update_payload) \
                           .eq("id", str(slot_id)) \
                           .execute()
        
        if response.count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability slot not found or update failed")
            
        # ⭐️ 최종 방어: 응답 dict를 jsonable_encoder로 감싸서 반환합니다. ⭐️
        return jsonable_encoder({"message": f"Slot {slot_id} updated successfully"})
    
    except Exception as e:
        print(f"🔥 PUT /api/availability/{slot_id} Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- 4. 삭제 (DELETE) API ---
@router.delete("/api/availability/{slot_id}")
def delete_availability_slot(slot_id: uuid.UUID):
    try:
        response = supabase.table('mentor_availability') \
                           .delete() \
                           .eq("id", str(slot_id)) \
                           .execute()
        
        if response.count == 0:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability slot not found")
            
        # ⭐️ 최종 방어: 응답 dict를 jsonable_encoder로 감싸서 반환합니다. ⭐️
        return jsonable_encoder({"message": f"Slot {slot_id} deleted successfully"})

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))