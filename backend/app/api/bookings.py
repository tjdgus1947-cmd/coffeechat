# backend/app/api/bookings.py

from fastapi import APIRouter, HTTPException, Depends
from app.core.config import supabase
from typing import List, Optional
from pydantic import BaseModel
from .auth import get_current_user_id
import uuid
from datetime import datetime 

router = APIRouter()

# =========================================
# ⬇️ Pydantic 모델 정의 (안전한 버전)
# =========================================

class UserSimple(BaseModel):
    full_name: Optional[str] = "알 수 없음" # 👈 데이터가 없어도 죽지 않도록 Optional 처리

class BookingReceived(BaseModel):
    id: int
    status: str
    # ⬇️ 멘티 정보가 없는 경우(탈퇴 등)에도 에러가 나지 않도록 Optional 적용
    mentee: Optional[UserSimple] = None 
    start_time: datetime  # 👈 추가: 예약 시작 시간
    end_time: datetime
    created_at: Optional[str] = None # 디버깅용

class BookingSent(BaseModel):
    id: int
    status: str
    mentor: Optional[UserSimple] = None
    created_at: Optional[str] = None

class BookingCreateRequest(BaseModel):
    mentor_id: str 
    availability_slot_id: str

class BookingStatusUpdate(BaseModel):
    status: str 

# =========================================
# ⬇️ API 라우트 함수 정의
# =========================================

@router.get("/api/bookings/received/me", response_model=List[BookingReceived])
def get_received_bookings_for_mentor(
    mentor_id: str = Depends(get_current_user_id)
):
    try:
        print(f"DEBUG: 멘토({mentor_id})의 받은 예약 조회 시도") # 👈 터미널 로그 확인용

        # 1. 쿼리 시도 (조인 문법이 맞는지 확인 필요)
        response = supabase.table('coffee_chats') \
            .select('id, status, start_time, end_time,created_at, mentee:users!mentee_id(full_name)') \
            .eq('mentor_id', mentor_id) \
            .order('created_at', desc=True) \
            .execute()
        
        # 2. 데이터 확인
        if response.data:
            print(f"DEBUG: DB 응답 데이터: {response.data}") # 👈 실제 DB에서 온 데이터 모양 확인
            return response.data
        return []

    except Exception as e:
        # ⭐️ 터미널에서 이 에러 메시지를 꼭 확인하세요!
        print(f"❌ Error fetching received bookings: {e}") 
        # Pydantic 모델 에러인지, DB 쿼리 에러인지 구분하기 위해 상세 출력
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@router.get("/api/bookings/me", response_model=List[BookingSent])
def get_sent_bookings_for_mentee(
    mentee_id: str = Depends(get_current_user_id)
):
    try:
        response = supabase.table('coffee_chats') \
            .select('id, status, created_at, mentor:users!mentor_id(full_name)') \
            .eq('mentee_id', mentee_id) \
            .order('created_at', desc=True) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching sent bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    update_data: BookingStatusUpdate,
    current_mentor_id: str = Depends(get_current_user_id)
):
    try:
        # 본인의 예약인지 확인
        check_response = supabase.table('coffee_chats') \
            .select('id') \
            .eq('id', booking_id) \
            .eq('mentor_id', current_mentor_id) \
            .execute()
            
        if not check_response.data:
             raise HTTPException(status_code=404, detail="예약을 찾을 수 없거나 권한이 없습니다.")

        # 상태 업데이트
        update_response = supabase.table('coffee_chats') \
            .update({'status': update_data.status}) \
            .eq('id', booking_id) \
            .select() \
            .execute()

        if not update_response.data:
             raise HTTPException(status_code=500, detail="상태 업데이트 실패")
             
        return {"message": f"예약 상태가 '{update_data.status}'로 변경되었습니다."}

    except Exception as e:
        print(f"Status Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))









# ... (나머지 create_booking, update_booking_status는 기존과 동일하게 유지)
@router.post("/api/bookings/create")
def create_booking(
    request: BookingCreateRequest,
    mentee_id: str = Depends(get_current_user_id) 
):
    try:
        # 1. 해당 슬롯이 '예약 가능' 상태인지 확인하고 '예약됨(True)'으로 변경
        slot_response = supabase.table('mentor_availability') \
            .update({'is_booked': True}) \
            .eq('id', request.availability_slot_id) \
            .eq('mentor_id', request.mentor_id) \
            .eq('is_booked', False) \
            .execute()
        
        if not slot_response.data:
            raise HTTPException(status_code=409, detail="이미 예약되었거나 유효하지 않은 시간입니다.")
        
        updated_slot = slot_response.data[0]

        # 2. coffee_chats 테이블에 예약 정보 생성
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
            raise HTTPException(status_code=500, detail="예약 생성에 실패했습니다.")

        return chat_response.data[0]

    except Exception as e:
        print(f"Booking Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class BookingStatusUpdate(BaseModel):
    status: str # 'approved' 또는 'rejected'

@router.put("/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    update_data: BookingStatusUpdate,
    mentor_id: str = Depends(get_current_user_id) # ⭐️ 현재 로그인한 멘토 ID
):
    """
    (멘토용) 멘토가 멘티의 신청(coffee_chat) 상태를
    'approved' 또는 'rejected'로 업데이트합니다.
    """
    if update_data.status not in ['approved', 'rejected']:
        raise HTTPException(status_code=400, detail="Invalid status value")

    try:
        # ⭐️ (보안)
        # 1. 'coffee_chats.id'가 booking_id와 일치하고
        # 2. 'coffee_chats.mentor_id'가 현재 로그인한 멘토의 ID와 일치하는 항목만
        # 3. 'status'를 'pending'에서 'approved' 또는 'rejected'로 변경합니다.
        
        response = supabase.table('coffee_chats') \
                           .update({'status': update_data.status}) \
                           .eq('id', booking_id) \
                           .eq('mentor_id', mentor_id) \
                           .eq('status', 'pending').execute()

        if response.count == 0:
            # 'pending' 상태가 아니거나, 내 예약이 아님
            raise HTTPException(status_code=404, detail="Booking not found, not pending, or permission denied.")
        
        print(f"예약 {booking_id} 상태 변경됨: {update_data.status}")
        return response.data[0]

    except Exception as e:
        print(f"심각한 오류 (예약 상태 변경): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))