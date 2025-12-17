# backend/app/api/bookings.py (수정됨)

from fastapi import APIRouter, HTTPException, Depends
from app.core.config import supabase
from typing import List, Optional
from pydantic import BaseModel
from .auth import get_current_user_id
import uuid
from datetime import datetime 
import traceback

router = APIRouter()

# --- Pydantic 모델 ---

class UserSimple(BaseModel):
    full_name: Optional[str] = "알 수 없음"

# 🔥 멘티 정보 추가 (멘토가 볼 수 있도록)
class MenteeDetailInfo(BaseModel):
    id: Optional[str] = None  # 🔥 [추가] 이 줄을 꼭 추가해주세요!
    full_name: Optional[str] = "알 수 없음"
    current_situation: Optional[str] = None
    career_goal: Optional[str] = None

class BookingReceived(BaseModel):
    id: str
    status: str
    mentee: Optional[MenteeDetailInfo] = None  # 🔥 상세 정보로 변경
    start_time: datetime
    end_time: datetime
    created_at: Optional[str] = None
    concern: Optional[str] = None  # 🔥 고민 필드 추가

class BookingSent(BaseModel):
    id: str
    status: str
    mentor: Optional[UserSimple] = None
    created_at: Optional[str] = None
    start_time: Optional[datetime] = None 
    end_time: Optional[datetime] = None
    concern: Optional[str] = None  # 🔥 고민 필드 추가

class BookingCreateRequest(BaseModel):
    mentor_id: str 
    availability_slot_id: str
    concern: Optional[str] = None  # 🔥 고민 필드 추가

class BookingStatusUpdate(BaseModel):
    status: str 

# --- API 라우트 ---

@router.get("/api/bookings/received/me", response_model=List[BookingReceived])
def get_received_bookings_for_mentor(
    mentor_id: str = Depends(get_current_user_id)
):
    """멘토가 받은 커피챗 신청 목록 조회 (멘티 상세 정보 포함)"""
    try:
        # 🔥 [수정됨] users 테이블 안에서 mentee_profiles를 찾도록 쿼리 구조 변경
        # 기존 코드: mentee_profiles!inner(...) -> 에러 원인 (직접 연결 없음)
        # 수정 코드: users(..., mentee_profiles(...)) -> 정상 (users를 통해 조회)
        
        response = supabase.table('coffee_chats') \
            .select('''
                id, status, start_time, end_time, created_at, concern, mentee_id,
                users!coffee_chats_mentee_id_fkey(
                    full_name,
                    mentee_profiles(current_situation, career_goal)
                )
            ''') \
            .eq('mentor_id', mentor_id) \
            .order('created_at', desc=True) \
            .execute()
        
        if response.data:
            transformed_data = []
            for item in response.data:
                # users 데이터 가져오기
                user_data = item.get('users') or {}
                
                # users 안에 중첩된 mentee_profiles 가져오기 (배열 형태일 수 있음)
                m_profile_data = user_data.get('mentee_profiles')
                
                # 배열이면 첫 번째 것, 객체면 그대로, 없으면 빈 딕셔너리
                if isinstance(m_profile_data, list) and m_profile_data:
                    profile = m_profile_data[0]
                elif isinstance(m_profile_data, dict):
                    profile = m_profile_data
                else:
                    profile = {}
                
                transformed_data.append({
                    'id': item['id'],
                    'status': item['status'],
                    'start_time': item['start_time'],
                    'end_time': item['end_time'],
                    'created_at': item['created_at'],
                    'concern': item.get('concern'),
                    'mentee': {
                        'id': item['mentee_id'],  # 🔥 [추가] 멘티 ID(UUID)를 여기에 맵핑!
                        'full_name': user_data.get('full_name', '알 수 없음'),
                        'current_situation': profile.get('current_situation'),
                        'career_goal': profile.get('career_goal')
                    }
                })
            return transformed_data
        return []
    
    except Exception as e:
        print(f"❌ 멘토 예약 조회 실패: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/bookings/me", response_model=List[BookingSent])
def get_sent_bookings_for_mentee(
    mentee_id: str = Depends(get_current_user_id)
):
    """멘티가 보낸 커피챗 신청 목록 조회"""
    try:
        response = supabase.table('coffee_chats') \
            .select('id, status, created_at, start_time, end_time, concern, mentor_id, users!coffee_chats_mentor_id_fkey(full_name)') \
            .eq('mentee_id', mentee_id) \
            .order('created_at', desc=True) \
            .execute()
        
        if response.data:
            transformed_data = []
            for item in response.data:
                data_item = {
                    'id': item['id'],
                    'status': item['status'],
                    'created_at': item['created_at'],
                    'start_time': item.get('start_time'),
                    'end_time': item.get('end_time'),
                    'concern': item.get('concern'),  # 🔥 고민 추가
                    'mentor': {
                        'full_name': item['users']['full_name'] if item.get('users') else '알 수 없음'
                    }
                }
                transformed_data.append(data_item)
            return transformed_data
            
        return []

    except Exception as e:
        print(f"❌ 멘티 예약 조회 실패: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/bookings/create")
def create_booking(
    request: BookingCreateRequest,
    mentee_id: str = Depends(get_current_user_id)
):
    """커피챗 예약 생성 (고민 포함)"""
    try:
        slot_check = supabase.table('mentor_availability') \
            .select('*') \
            .eq('id', request.availability_slot_id) \
            .execute()

        if not slot_check.data:
            raise HTTPException(status_code=404, detail="예약 가능한 슬롯을 찾을 수 없습니다.")

        slot = slot_check.data[0]

        if slot['is_booked']:
            raise HTTPException(status_code=409, detail="이미 예약된 시간 슬롯입니다.")

        existing = supabase.table('coffee_chats') \
            .select('id') \
            .eq('availability_id', request.availability_slot_id) \
            .execute()

        if existing.data:
            raise HTTPException(status_code=409, detail="이미 해당 슬롯에 예약이 존재합니다.")
        
        mentor_profile = supabase.table("mentor_profiles").select("user_id").eq("id", request.mentor_id).single().execute()
        real_mentor_id = mentor_profile.data['user_id']

        # 🔥 concern 필드 추가
        chat_response = supabase.table('coffee_chats').insert({
            'id': str(uuid.uuid4()),
            'mentee_id': mentee_id,
            'mentor_id': real_mentor_id,
            'availability_id': request.availability_slot_id,
            'status': 'pending',
            'start_time': slot['start_time'],
            'end_time': slot['end_time'],
            'concern': request.concern  # 🔥 고민 저장
        }).execute()
        
        if not chat_response.data:
            raise HTTPException(status_code=500, detail="예약 정보 삽입에 실패했습니다.")
            
        supabase.table('mentor_availability') \
            .update({'is_booked': True}) \
            .eq('id', request.availability_slot_id) \
            .execute()

        return chat_response.data[0]

    except Exception as e:
        print(f"❌ 예약 생성 중 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: str,
    update_data: BookingStatusUpdate,
    current_mentor_id: str = Depends(get_current_user_id)
):
    """커피챗 승인/거절 처리 + 채팅방 생성"""
    try:
        check_response = supabase.table('coffee_chats') \
            .select('id, availability_id, mentor_id, mentee_id') \
            .eq('id', booking_id) \
            .eq('mentor_id', current_mentor_id) \
            .execute()
            
        if not check_response.data:
            raise HTTPException(status_code=404, detail="권한이 없거나 예약을 찾을 수 없습니다.")

        booking_info = check_response.data[0]
        slot_id = booking_info.get('availability_id')

        update_payload = {'status': update_data.status}
        
        if update_data.status in ['approved', 'rejected']:
            update_payload['availability_id'] = None 

        update_response = supabase.table('coffee_chats') \
            .update(update_payload) \
            .eq('id', booking_id) \
            .execute()

        # 🔥 승인 시 채팅방 생성
        if update_data.status == 'approved':
            try:
                chat_room_response = supabase.table('chat_rooms').insert({
                    'coffee_chat_id': booking_id,
                    'mentor_id': booking_info['mentor_id'],
                    'mentee_id': booking_info['mentee_id']
                }).execute()
                
                print(f"✅ 채팅방 생성 완료: {chat_room_response.data}")
            except Exception as chat_error:
                print(f"⚠️ 채팅방 생성 실패 (예약은 승인됨): {chat_error}")

        if update_data.status in ['approved', 'rejected']:
            if slot_id:
                supabase.table('mentor_availability') \
                    .delete() \
                    .eq('id', slot_id) \
                    .execute()

        return {"message": f"예약이 {update_data.status} 처리되었습니다."}

    except Exception as e:
        print(f"🔥 상태 업데이트 실패: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))