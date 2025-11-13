from fastapi import APIRouter, HTTPException, Depends
from app.core.config import supabase
from typing import List
from pydantic import BaseModel
# 1. auth.py에서 '로그인한 유저의 ID'를 가져오는 헬퍼 함수를 임포트합니다.
from .auth import get_current_user_id

router = APIRouter()

# --- Pydantic 응답 모델 정의 ---
# API가 프론트엔드에 반환할 데이터 형식을 지정합니다.

class UserSimple(BaseModel):
    """
    Join을 통해 가져올 최소한의 유저 정보 (멘토 또는 멘티)
    """
    full_name: str
    avatar_url: str | None = None
    # (필요시) email: str | None = None

class BookingReceived(BaseModel):
    """
    멘토가 '받은' 신청 목록을 위한 응답 모델
    """
    id: int
    status: str
    mentee: UserSimple # 멘티 정보가 중첩된 객체로 들어옴

class BookingSent(BaseModel):
    """
    멘티가 '보낸' 신청 목록을 위한 응답 모델
    """
    id: int
    status: str
    mentor: UserSimple # 멘토 정보가 중첩된 객체로 들어옴


# --- 1. (멘토용) 멘토가 받은 신청 목록 API ---
# (기존 코드와 동일 - 프론트엔드 mentorStore.js와 연동)
@router.get(
    "/api/bookings/received/me", 
    response_model=List[BookingReceived] # 응답 형식은 BookingReceived 모델의 리스트
)
def get_received_bookings_for_mentor(
    # 이 API는 로그인이 필요하며, 'mentor_id'에 로그인한 유저의 UUID가 들어옵니다.
    mentor_id: str = Depends(get_current_user_id)
):
    """
    (멘토용) 현재 로그인한 멘토(mentor_id)가 'coffee_chats' 테이블에서
    받은 모든 신청 목록을 멘티 정보와 Join하여 반환합니다.
    """
    try:
        print(f"멘토 대시보드 API 수신: 멘토 ID {mentor_id}")

        # Supabase 쿼리:
        # "coffee_chats 테이블에서 '멘토id'가 나와 같은 것을 찾고,
        #  거기에 '멘티id'에 해당하는 'users' 테이블의 'full_name'을 
        #  'mentee'라는 이름의 객체로 붙여줘"
        response = supabase.table('coffee_chats') \
            .select('id, status, mentee:users!coffee_chats_mentee_id_fkey(full_name, avatar_url)') \
            .eq('mentor_id', mentor_id) \
            .order('created_at', desc=True) \
            .execute()

        if response.data:
            print(f"멘토({mentor_id})에게 {len(response.data)}건의 신청 발견")
            return response.data
        
        print(f"멘토({mentor_id})에게 온 신청 없음")
        return []

    except Exception as e:
        print(f"심각한 오류 (멘토 대시보드): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 2. (멘티용) 멘티가 보낸 신청 목록 API ---
# (신규 추가 - 프론트엔드 bookingstore.js와 연동)
@router.get(
    "/api/bookings/me", 
    response_model=List[BookingSent] # 응답 형식은 BookingSent 모델의 리스트
)
def get_sent_bookings_for_mentee(
    # 이 API는 로그인이 필요하며, 'mentee_id'에 로그인한 유저의 UUID가 들어옵니다.
    mentee_id: str = Depends(get_current_user_id)
):
    """
    (멘티용) 현재 로그인한 멘티(mentee_id)가 'coffee_chats' 테이블에서
    '보낸' 모든 신청 목록을 멘토 정보와 Join하여 반환합니다.
    """
    try:
        print(f"멘티 마이페이지 API 수신: 멘티 ID {mentee_id}")

        # Supabase 쿼리:
        # "coffee_chats 테이블에서 '멘티id'가 나와 같은 것을 찾고,
        #  거기에 '멘토id'에 해당하는 'users' 테이블의 'full_name'을 
        #  'mentor'라는 이름의 객체로 붙여줘"
        response = supabase.table('coffee_chats') \
            .select('id, status, mentor:users!coffee_chats_mentor_id_fkey(full_name, avatar_url)') \
            .eq('mentee_id', mentee_id) \
            .order('created_at', desc=True) \
            .execute()

        if response.data:
            print(f"멘티({mentee_id})가 보낸 {len(response.data)}건의 신청 발견")
            return response.data
        
        print(f"멘티({mentee_id})가 보낸 신청 없음")
        return []

    except Exception as e:
        print(f"심각한 오류 (멘티 마이페이지): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# (wbs_detail.md) (추후 구현)
# @router.post("/bookings/approve/{chat_id}")
# def approve_booking(chat_id: int, mentor_id: str = Depends(get_current_user_id)):
#     # ... (coffee_chats.id == chat_id 이고, coffee_chats.멘토id == mentor_id 인지 확인 후)
#     # ... (status를 'approved'로 UPDATE)
#     pass

# @router.post("/bookings/reject/{chat_id}")
# def reject_booking(chat_id: int, mentor_id: str = Depends(get_current_user_id)):
#     # ... (status를 'rejected'로 UPDATE)
#     pass