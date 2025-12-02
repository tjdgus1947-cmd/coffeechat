# File: backend/app/api/coffeechats.py
# (WBS 6.2: 커피챗 예약 기능 - Pydantic 스키마 키 이름 수정)

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.core.config import supabase
import uuid
from datetime import datetime
from fastapi.encoders import jsonable_encoder

router = APIRouter()

# --- 스키마 정의 (cURL과 일치하도록 mentor_id 사용) ---
class CoffeeChatBooking(BaseModel):
    mentee_user_id: uuid.UUID # 👈 public.users.id
    mentor_id: uuid.UUID      # 👈 ⭐️ mentor_profiles.id (키 이름을 mentor_id로 변경)
    availability_slot_id: uuid.UUID # 👈 mentor_availability.id

# --- 1. 커피챗 예약 생성 (POST) API ---
@router.post("/api/coffeechats/book")
def create_coffeechat_booking(booking: CoffeeChatBooking):
    """
    멘티가 특정 멘토의 가용 시간 슬롯에 커피챗을 신청합니다.
    (WBS 6.2)
    """
    try:
        # 1. 멘티의 'user_id'로 'mentee_profiles.id'를 조회
        profile_response_mentee = supabase.table('mentee_profiles') \
                                 .select('id') \
                                 .eq('user_id', str(booking.mentee_user_id)) \
                                 .limit(1) \
                                 .execute()

        if not profile_response_mentee.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentee profile not found for the given user_id.")
        
        actual_mentee_profile_id = profile_response_mentee.data[0]['id']
        
        # ⭐️ 2. 멘토 ID는 받은 'mentor_id' (profile_id)를 그대로 사용
        actual_mentor_profile_id = str(booking.mentor_id)

        # 3. 멘토 가용 슬롯 상태 업데이트: is_booked = True
        slot_update_response = (
            supabase.table('mentor_availability') 
            .update({"is_booked": True}) 
            .eq("id", str(booking.availability_slot_id)) 
            .eq("is_booked", False) # 예약되지 않은 슬롯만 예약 가능
            .execute()
        )

        if slot_update_response.count == 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is already booked or invalid ID.")

        # 4. coffee_chats 테이블에 예약 정보 삽입
        chat_insert_response = (
            supabase.table('coffee_chats').insert({
                "mentee_id": str(actual_mentee_profile_id), 
                "mentor_id": actual_mentor_profile_id,      
                "availability_slot_id": str(booking.availability_slot_id),
                "status": "pending", 
            }).execute()
        )

        if not chat_insert_response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create coffee chat record.")
            
        return jsonable_encoder(chat_insert_response.data[0])

    except HTTPException as h:
        raise h
    except Exception as e:
        print(f"🔥 Coffee Chat Booking Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))