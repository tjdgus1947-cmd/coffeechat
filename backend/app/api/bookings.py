# backend/app/api/bookings.py

from fastapi import APIRouter, HTTPException, Depends
from app.core.config import supabase
from typing import List
from pydantic import BaseModel
from .auth import get_current_user_id
import uuid
from datetime import datetime 

router = APIRouter()

# =========================================
# ⬇️ Pydantic 모델 정의 (반드시 함수보다 위에 있어야 함)
# =========================================

class UserSimple(BaseModel):
    full_name: str

class BookingReceived(BaseModel):
    id: int
    status: str
    mentee: UserSimple

class BookingSent(BaseModel):
    id: int
    status: str
    mentor: UserSimple

class BookingCreateRequest(BaseModel):
    mentor_id: str 
    availability_slot_id: str 

# =========================================
# ⬇️ API 라우트 함수 정의
# =========================================

@router.get("/api/bookings/received/me", response_model=List[BookingReceived])
def get_received_bookings_for_mentor(
    mentor_id: str = Depends(get_current_user_id)
):
    try:
        response = supabase.table('coffee_chats') \
            .select('id, status, mentee:users(full_name)') \
            .eq('mentor_id', mentor_id) \
            .order('created_at', desc=True) \
            .execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/bookings/me", response_model=List[BookingSent])
def get_sent_bookings_for_mentee(
    mentee_id: str = Depends(get_current_user_id)
):
    try:
        response = supabase.table('coffee_chats') \
            .select('id, status, mentor:users(full_name)') \
            .eq('mentee_id', mentee_id) \
            .order('created_at', desc=True) \
            .execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/bookings/create")
def create_booking(
    request: BookingCreateRequest,  # 👈 이제 위에서 정의했기 때문에 에러가 나지 않습니다.
    mentee_id: str = Depends(get_current_user_id) 
):
    try:
        # 1. 슬롯을 '예약됨(True)'으로 변경
        slot_response = supabase.table('mentor_availability') \
            .update({'is_booked': True}) \
            .eq('id', request.availability_slot_id) \
            .eq('mentor_id', request.mentor_id) \
            .eq('is_booked', False) \
            .execute()
        
        if not slot_response.data:
            raise HTTPException(status_code=409, detail="Slot is already booked or not found")
        
        updated_slot = slot_response.data[0]

        # 2. coffee_chats에 '승인 대기' 상태로 기록
        chat_response = supabase.table('coffee_chats') \
            .insert({
                'mentee_id': mentee_id,
                'mentor_id': request.mentor_id,
                'availability_id': request.availability_slot_id,
                'status': 'pending',
                'start_time': updated_slot['start_time'],
                'end_time': updated_slot['end_time']
            }) \
            .execute()

        if not chat_response.data:
            raise HTTPException(status_code=500, detail="Failed to create coffee chat record")

        return chat_response.data[0]

    except Exception as e:
        print(f"Booking Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))