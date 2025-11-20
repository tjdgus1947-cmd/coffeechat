# backend/app/api/bookings.py (디버깅 모드)

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

class BookingReceived(BaseModel):
    id: str
    status: str
    mentee: Optional[UserSimple] = None 
    start_time: datetime
    end_time: datetime
    created_at: Optional[str] = None

# 🔥 [확인] 여기에 start_time, end_time이 있어야 함
class BookingSent(BaseModel):
    id: str
    status: str
    mentor: Optional[UserSimple] = None
    created_at: Optional[str] = None
    start_time: Optional[datetime] = None 
    end_time: Optional[datetime] = None   

class BookingCreateRequest(BaseModel):
    mentor_id: str 
    availability_slot_id: str

class BookingStatusUpdate(BaseModel):
    status: str 

# --- API 라우트 ---

@router.get("/api/bookings/received/me", response_model=List[BookingReceived])
def get_received_bookings_for_mentor(
    mentor_id: str = Depends(get_current_user_id)
):
    # (멘토용 코드는 생략 - 기존과 동일)
    try:
        response = supabase.table('coffee_chats') \
            .select('id, status, start_time, end_time, created_at, mentee_id, users!coffee_chats_mentee_id_fkey(full_name)') \
            .eq('mentor_id', mentor_id) \
            .order('created_at', desc=True) \
            .execute()
        
        if response.data:
            transformed_data = []
            for item in response.data:
                transformed_data.append({
                    'id': item['id'],
                    'status': item['status'],
                    'start_time': item['start_time'],
                    'end_time': item['end_time'],
                    'created_at': item['created_at'],
                    'mentee': { 'full_name': item['users']['full_name'] if item.get('users') else '알 수 없음' }
                })
            return transformed_data
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔥🔥🔥 [여기가 문제의 구간입니다] 🔥🔥🔥
@router.get("/api/bookings/me", response_model=List[BookingSent])
def get_sent_bookings_for_mentee(
    mentee_id: str = Depends(get_current_user_id)
):
    try:
        print(f"\n🔍 [디버깅] 멘티 예약 조회 시작: ID={mentee_id}")
        
        # 1. DB에서 데이터 가져오기
        response = supabase.table('coffee_chats') \
            .select('id, status, created_at, start_time, end_time, mentor_id, users!coffee_chats_mentor_id_fkey(full_name)') \
            .eq('mentee_id', mentee_id) \
            .order('created_at', desc=True) \
            .execute()
        
        # 2. DB에서 가져온 원본 데이터 확인
        print(f"📊 [디버깅] DB 응답 개수: {len(response.data)}")
        if response.data:
            print(f"📝 [디버깅] 첫 번째 데이터 샘플: {response.data[0]}") 
            # 👆 터미널에서 이 부분에 'start_time'이 있는지 꼭 확인하세요!

            transformed_data = []
            for item in response.data:
                data_item = {
                    'id': item['id'],
                    'status': item['status'],
                    'created_at': item['created_at'],
                    'start_time': item.get('start_time'), # 여기서 매핑
                    'end_time': item.get('end_time'),
                    'mentor': {
                        'full_name': item['users']['full_name'] if item.get('users') else '알 수 없음'
                    }
                }
                transformed_data.append(data_item)
            
            print(f"🚀 [디버깅] 변환 후 데이터 (첫번째): {transformed_data[0]}")
            return transformed_data
            
        return []

    except Exception as e:
        print(f"❌ [디버깅] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# (나머지 create_booking 등의 코드는 기존 유지)
@router.post("/api/bookings/create")
def create_booking(
    request: BookingCreateRequest,
    mentee_id: str = Depends(get_current_user_id)
):
    try:
        # 1️⃣ 해당 슬롯 조회
        slot_check = supabase.table('mentor_availability') \
            .select('*') \
            .eq('id', request.availability_slot_id) \
            .execute()

        if not slot_check.data:
            raise HTTPException(status_code=404, detail="예약 가능한 슬롯을 찾을 수 없습니다.")

        slot = slot_check.data[0]
        print(f"🕒 [디버깅] 슬롯 정보 확인: start_time={slot.get('start_time')}") # 디버깅용

        if slot['is_booked']:
            raise HTTPException(status_code=409, detail="이미 예약된 시간 슬롯입니다.")

        existing = supabase.table('coffee_chats') \
            .select('id') \
            .eq('availability_id', request.availability_slot_id) \
            .execute()

        if existing.data:
            raise HTTPException(status_code=409, detail="이미 해당 슬롯에 예약이 존재합니다.")
        
        # 멘토 ID 찾기
        mentor_profile = supabase.table("mentor_profiles").select("user_id").eq("id", request.mentor_id).single().execute()
        real_mentor_id = mentor_profile.data['user_id']

        # 예약 생성
        chat_response = supabase.table('coffee_chats').insert({
                'id': str(uuid.uuid4()),
                'mentee_id': mentee_id,
                'mentor_id': real_mentor_id,
                'availability_id': request.availability_slot_id,
                'status': 'pending',
                'start_time': slot['start_time'],
                'end_time': slot['end_time']
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
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: str,
    update_data: BookingStatusUpdate,
    current_mentor_id: str = Depends(get_current_user_id)
):
    # (기존 코드 유지)
    try:
        check_response = supabase.table('coffee_chats').select('id').eq('id', booking_id).eq('mentor_id', current_mentor_id).execute()
        if not check_response.data:
            raise HTTPException(status_code=404, detail="권한 없음")

        update_response = supabase.table('coffee_chats').update({'status': update_data.status}).eq('id', booking_id).execute()
        return {"message": "상태 업데이트 성공"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))