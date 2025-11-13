# backend/app/api/booking.py
# (wbs.md 6.0[cite: wbs.md] 커피챗 예약 API)

from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.core.config import supabase
import uuid

# (참고: 님의 auth.py[cite: backend/app/api/auth.py] 코드를 기반으로, 
#  '수민'님의 auth.js가 JWT 토큰을 헤더에 보낼 것이라고 가정합니다.)
#  실제 프로덕션에서는 이 token을 검증하는 로직이 필요합니다.
#  (예: def get_current_user(token: str = Depends(oauth2_scheme)) ...)

router = APIRouter()

# --- 1. 커피챗 예약 생성 API ---

class CoffeeChatBooking(BaseModel):
    # '수민'님의 BookingCalendar.vue가 보내야 할 데이터
    mentor_id: uuid.UUID # 멘토 프로필 ID (mentor_profiles.id[cite: setup_v2.sql])
    mentee_user_id: uuid.UUID # 멘티 유저 ID (public.users.id[cite: setup_v2.sql])
    availability_slot_id: uuid.UUID # 멘토가 가능한 시간 ID

@router.post("/api/coffee-chats/")
async def create_coffee_chat_booking(booking: CoffeeChatBooking):
    """
    (wbs.md 6.2)[cite: wbs.md] 멘티가 멘토에게 커피챗을 신청합니다.
    (image_74b795.png[cite: uploaded:image_74b795.png]의 '예약 확정' 버튼이 호출할 API)
    
    이 API는 3가지 작업을 수행합니다:
    1. 멘티의 profile_id를 조회합니다.
    2. mentor_availability[cite: setup_v2.sql] 테이블의 슬롯을 'is_booked = true'로 업데이트합니다.
    3. coffee_chats[cite: setup_v2.sql] 테이블에 'pending' 상태로 새 예약을 생성합니다.
    """
    try:
        # 1. 멘티의 user_id로 mentee_profiles[cite: setup_v2.sql]의 id(PK)를 조회
        mentee_profile_res = supabase.table('mentee_profiles') \
                                     .select('id') \
                                     .eq('user_id', str(booking.mentee_user_id)) \
                                     .limit(1) \
                                     .execute()
        
        if not mentee_profile_res.data:
            raise HTTPException(status_code=404, detail="Mentee profile not found for this user")
            
        mentee_profile_id = mentee_profile_res.data[0]['id']

        # 2. (Transaction 1) 멘토의 시간 슬롯을 '예약됨'으로 업데이트
        slot_update_res = supabase.table('mentor_availability') \
                                  .update({'is_booked': True}) \
                                  .eq('id', str(booking.availability_slot_id)) \
                                  .eq('is_booked', False) \
                                  .select() \
                                  .execute()
        
        if not slot_update_res.data:
            raise HTTPException(status_code=409, detail="Slot just got booked or does not exist")

        # 3. (Transaction 2) coffee_chats[cite: setup_v2.sql] 테이블에 새 예약 생성
        booking_res = supabase.table('coffee_chats').insert({
            "mentee_id": mentee_profile_id,
            "mentor_id": str(booking.mentor_id),
            "availability_slot_id": str(booking.availability_slot_id),
            "status": 'pending' # 'pending' (대기중) 상태로 예약 생성
        }).select().execute()

        if not booking_res.data:
            raise HTTPException(status_code=500, detail="Failed to create booking")

        return booking_res.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. "내 예약 목록" 조회 API (멘티용) ---

@router.get("/api/coffee-chats/me/{mentee_user_id}")
def get_my_bookings(mentee_user_id: uuid.UUID):
    """
    (wbs.md 7.1)[cite: wbs.md] 멘티가 "마이페이지"에서 본인의 예약 목록을 조회합니다.
    (image_74b7b6.png[cite: uploaded:image_74b7b6.png] 화면이 호출할 API)
    
    이 API는 3개 테이블을 JOIN합니다:
    1. mentee_profiles[cite: setup_v2.sql] (user_id로 본인 찾기)
    2. coffee_chats[cite: setup_v2.sql] (예약 목록)
    3. mentor_profiles[cite: setup_v2.sql] (멘토 정보)
    4. public.users[cite: setup_v2.sql] (멘토 이름)
    """
    try:
        # 1. 멘티의 user_id로 mentee_profiles[cite: setup_v2.sql]의 id(PK)를 조회
        mentee_profile_res = supabase.table('mentee_profiles') \
                                     .select('id') \
                                     .eq('user_id', str(mentee_user_id)) \
                                     .limit(1) \
                                     .execute()
        
        if not mentee_profile_res.data:
            raise HTTPException(status_code=404, detail="Mentee profile not found for this user")
            
        mentee_profile_id = mentee_profile_res.data[0]['id']

        # 2. mentee_profile_id로 coffee_chats[cite: setup_v2.sql] 목록을 조회 (JOIN)
        # (복잡한 JOIN을 위해 RPC 함수를 만드는 것이 좋으나, 우선 간단히 구현)
        response = supabase.table('coffee_chats') \
                           .select('*, mentor_profiles(user_id, mentor_profiles(full_name:users(full_name)))') \
                           .eq('mentee_id', mentee_profile_id) \
                           .order('created_at', desc=True) \
                           .execute()
        
        # (참고: 위 .select() 구문은 Supabase의 Foreign Key 관계에 의존합니다.
        #  ERD[cite: setup_v2.sql]가 정확하다면, 멘토의 full_name까지 가져옵니다.)

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))