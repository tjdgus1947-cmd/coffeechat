# backend/app/api/bookings.py
# (수정: 조인 문법 및 디버깅 강화)

from fastapi import APIRouter, HTTPException, Depends
from app.core.config import supabase
from typing import List, Optional
from pydantic import BaseModel
from .auth import get_current_user_id
import uuid
from datetime import datetime 

router = APIRouter()

# =========================================
# Pydantic 모델 정의
# =========================================

class UserSimple(BaseModel):
    full_name: Optional[str] = "알 수 없음"

class BookingReceived(BaseModel):
    id: str  # 👈 UUID는 문자열
    status: str
    mentee: Optional[UserSimple] = None 
    start_time: datetime
    end_time: datetime
    created_at: Optional[str] = None

class BookingSent(BaseModel):
    id: str  # 👈 UUID는 문자열
    status: str
    mentor: Optional[UserSimple] = None
    created_at: Optional[str] = None

class BookingCreateRequest(BaseModel):
    mentor_id: str 
    availability_slot_id: str

class BookingStatusUpdate(BaseModel):
    status: str 

# =========================================
# API 라우트
# =========================================

@router.get("/api/bookings/received/me", response_model=List[BookingReceived])
def get_received_bookings_for_mentor(
    mentor_id: str = Depends(get_current_user_id)
):
    """
    멘토가 받은 커피챗 신청 목록 조회
    """
    try:
        print(f"🔍 DEBUG: 멘토 ID = {mentor_id}")
        
        # 1단계: 기본 쿼리 (조인 없이)
        print("📊 1단계: 기본 데이터 조회 시도...")
        basic_response = supabase.table('coffee_chats') \
            .select('*') \
            .eq('mentor_id', mentor_id) \
            .execute()
        
        print(f"✅ 기본 쿼리 결과: {len(basic_response.data) if basic_response.data else 0}건")
        print(f"📋 원본 데이터: {basic_response.data}")
        
        # 2단계: 조인 쿼리
        print("📊 2단계: 멘티 정보 조인 시도...")
        
        # ⭐ Supabase 조인 문법 수정
        response = supabase.table('coffee_chats') \
            .select('id, status, start_time, end_time, created_at, mentee_id, users!coffee_chats_mentee_id_fkey(full_name)') \
            .eq('mentor_id', mentor_id) \
            .order('created_at', desc=True) \
            .execute()
        
        print(f"✅ 조인 쿼리 결과: {response.data}")
        
        if response.data:
            # 데이터 변환 (Supabase 조인 결과 구조에 맞춤)
            transformed_data = []
            for item in response.data:
                transformed_item = {
                    'id': item['id'],
                    'status': item['status'],
                    'start_time': item['start_time'],
                    'end_time': item['end_time'],
                    'created_at': item['created_at'],
                    'mentee': {
                        'full_name': item['users']['full_name'] if item.get('users') else '알 수 없음'
                    }
                }
                transformed_data.append(transformed_item)
            
            print(f"✅ 변환된 데이터: {transformed_data}")
            return transformed_data
        
        print("⚠️ 데이터 없음")
        return []

    except Exception as e:
        print(f"❌ 심각한 오류: {type(e).__name__}")
        print(f"❌ 오류 메시지: {str(e)}")
        import traceback
        print(f"❌ 전체 스택: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/api/bookings/me", response_model=List[BookingSent])
def get_sent_bookings_for_mentee(
    mentee_id: str = Depends(get_current_user_id)
):
    try:
        print(f"🔍 멘티 예약 조회: {mentee_id}")
        
        response = supabase.table('coffee_chats') \
            .select('id, status, created_at, mentor_id, users!coffee_chats_mentor_id_fkey(full_name)') \
            .eq('mentee_id', mentee_id) \
            .order('created_at', desc=True) \
            .execute()
        
        if response.data:
            transformed_data = []
            for item in response.data:
                transformed_data.append({
                    'id': item['id'],
                    'status': item['status'],
                    'created_at': item['created_at'],
                    'mentor': {
                        'full_name': item['users']['full_name'] if item.get('users') else '알 수 없음'
                    }
                })
            return transformed_data
            
        return []
    except Exception as e:
        print(f"❌ 멘티 예약 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/bookings/create")
def create_booking(
    request: BookingCreateRequest,
    mentee_id: str = Depends(get_current_user_id) 
):
    try:
        # 슬롯 예약
        slot_response = supabase.table('mentor_availability') \
            .update({'is_booked': True}) \
            .eq('id', request.availability_slot_id) \
            .eq('mentor_id', request.mentor_id) \
            .eq('is_booked', False) \
            .execute()
        
        if not slot_response.data:
            raise HTTPException(status_code=409, detail="이미 예약되었거나 유효하지 않은 시간입니다.")
        
        updated_slot = slot_response.data[0]

        # 예약 생성
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
        print(f"❌ 예약 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: str,  # 👈 UUID는 문자열
    update_data: BookingStatusUpdate,
    current_mentor_id: str = Depends(get_current_user_id)
):
    """
    멘토가 예약 상태를 승인/거절
    """
    try:
        print(f"🔄 상태 업데이트 시도: booking_id={booking_id}, status={update_data.status}")
        
        # 권한 확인
        check_response = supabase.table('coffee_chats') \
            .select('id, status') \
            .eq('id', booking_id) \
            .eq('mentor_id', current_mentor_id) \
            .execute()
            
        if not check_response.data:
            raise HTTPException(status_code=404, detail="예약을 찾을 수 없거나 권한이 없습니다.")

        print(f"✅ 권한 확인 완료: {check_response.data}")

        # 상태 업데이트
        update_response = supabase.table('coffee_chats') \
            .update({'status': update_data.status}) \
            .eq('id', booking_id) \
            .execute()

        if not update_response.data:
            raise HTTPException(status_code=500, detail="상태 업데이트 실패")
        
        print(f"✅ 상태 업데이트 성공: {update_response.data}")
        return {"message": f"예약 상태가 '{update_data.status}'로 변경되었습니다."}

    except Exception as e:
        print(f"❌ 상태 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))