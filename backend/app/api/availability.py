# backend/app/api/availability.py
# (wbs.md 6.1[cite: wbs.md] 멘토 일정 관리 API)

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.core.config import supabase
import uuid

router = APIRouter()

# --- 1. 멘토가 "가능한 시간"을 등록/수정/삭제하는 API ---

class AvailabilitySlot(BaseModel):
    mentor_id: uuid.UUID # (ERD: mentor_profiles.id[cite: setup_v2.sql])
    start_time: datetime
    end_time: datetime

@router.post("/api/availability/")
def create_availability_slot(slot: AvailabilitySlot):
    """
    멘토가 "커피챗 가능한 시간" 1개를 DB에 등록합니다.
    (wbs.md 6.1)[cite: wbs.md]
    (참고: '수민'님의 캘린더 UI에는 아직 이 API를 호출하는 폼이 없습니다.)
    """
    try:
        response = supabase.table('mentor_availability').insert({
            "mentor_id": str(slot.mentor_id),
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "is_booked": False
        }).select().execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create availability slot")
            
        return response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# (wbs.md 6.1[cite: wbs.md]에는 DELETE, UPDATE API도 필요하지만, 우선 GET부터 구현합니다)

# --- 2. 멘티가 "가능한 시간"을 조회하는 API ---

@router.get("/api/availability/{mentor_id}")
def get_mentor_availability(mentor_id: uuid.UUID):
    """
    '수민'님의 BookingCalendar.vue가 호출할 API입니다.
    특정 멘토의 "예약되지 않은(is_booked = false)" 모든 시간 슬롯을 반환합니다.
    (wbs.md 6.1)[cite: wbs.md]
    """
    try:
        response = supabase.table('mentor_availability') \
                           .select("id, start_time, end_time") \
                           .eq('mentor_id', str(mentor_id)) \
                           .eq('is_booked', False) \
                           .gte('start_time', datetime.now().isoformat()) \
                           .order('start_time', desc=False) \
                           .execute()
        
        # (참고: BookingCalendar.vue는 {'2025-11-18': ['14:00', '15:00']} 형식을 기대하지만,
        #  우선 DB 데이터를 그대로 반환하고, '수민'님이 프론트엔드에서 가공합니다.)
        
        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))