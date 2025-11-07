from fastapi import APIRouter, HTTPException, Body, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta # ⭐️ timedelta 임포트
from app.core.config import supabase
import uuid
from fastapi.encoders import jsonable_encoder 

router = APIRouter()

# --- 스키마 정의 ---

# ⭐️ [수정됨] 프론트엔드에서 받을 스키마
class AvailabilityCreate(BaseModel):
    user_id: uuid.UUID  # ⭐️ auth.users.id를 받습니다. (mentor_id 대신)
    start_time: datetime
    end_time: datetime

class AvailabilityUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# ⭐️ [신규] 멘토 프로필 ID를 찾는 헬퍼 함수
def get_mentor_profile_id(user_id: uuid.UUID) -> uuid.UUID:
    """auth.users.id를 사용하여 mentor_profiles.id (PK)를 찾습니다."""
    try:
        profile_res = supabase.table("mentor_profiles") \
            .select("id") \
            .eq("user_id", str(user_id)) \
            .single() \
            .execute()

        if not profile_res.data:
            raise HTTPException(status_code=404, detail="멘토 프로필을 찾을 수 없습니다.")
        
        return profile_res.data['id']
    except Exception as e:
        print(f"🔥 get_mentor_profile_id 오류: {e}")
        raise HTTPException(status_code=500, detail=f"멘토 프로필 조회 실패: {str(e)}")

# --- 1. 생성 (POST) API ---
@router.post("/api/availability/")
def create_availability_slot(slot: AvailabilityCreate): # ⭐️ 스키마 변경
    try:
        # ⭐️ [수정됨] user_id로 mentor_id (PK) 찾기
        mentor_profile_id = get_mentor_profile_id(slot.user_id)
        
        response = supabase.table('mentor_availability').insert({
            "mentor_id": str(mentor_profile_id), # ⭐️ 찾은 멘토 프로필 ID 사용
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
@router.get("/api/availability/{user_id}") # ⭐️ mentor_id가 아닌 user_id로 변경
def get_mentor_availability(user_id: uuid.UUID): # ⭐️ user_id로 변경
    try:
        # ⭐️ [수정됨] user_id로 mentor_id (PK) 찾기
        mentor_profile_id = get_mentor_profile_id(user_id)
        
        response = supabase.table('mentor_availability') \
                            .select("*") \
                            .eq('mentor_id', str(mentor_profile_id)) \
                            .eq('is_booked', False) \
                            .gte('start_time', datetime.now().isoformat()) \
                            .order('start_time', desc=False) \
                            .execute()
        
        return jsonable_encoder(response.data)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# --- 3. 수정 (PUT) API ---
# (이 엔드포인트는 일단 변경 없이 유지)
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
            
        return jsonable_encoder({"message": f"Slot {slot_id} updated successfully"})
    
    except Exception as e:
        print(f"🔥 PUT /api/availability/{slot_id} Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- 4. 삭제 (DELETE) API ---
# (이 엔드포인트는 변경 없이 유지)
@router.delete("/api/availability/{slot_id}")
def delete_availability_slot(slot_id: uuid.UUID):
    try:
        response = supabase.table('mentor_availability') \
                            .delete() \
                            .eq("id", str(slot_id)) \
                            .execute()
        
        if response.count == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability slot not found")
            
        return jsonable_encoder({"message": f"Slot {slot_id} deleted successfully"})

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))