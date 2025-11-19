# app/api/availability.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.core.config import supabase
from fastapi.encoders import jsonable_encoder

router = APIRouter()


# ----- 스키마 -----

class AvailabilityCreate(BaseModel):
    user_id: uuid.UUID        # auth.users.id (멘토 유저 ID)
    start_time: datetime
    end_time: datetime


class AvailabilityUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# ----- 헬퍼 함수 -----

def get_mentor_profile_id(user_id: uuid.UUID) -> uuid.UUID:
    """
    auth.users.id(user_id)로 mentor_profiles.id(PK) 조회
    """
    try:
        profile_res = (
            supabase.table("mentor_profiles")
            .select("id")
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )

        if not profile_res.data:
            raise HTTPException(
                status_code=404,
                detail="멘토 프로필을 찾을 수 없습니다.",
            )

        return profile_res.data["id"]

    except HTTPException:
        # 위에서 이미 HTTPException을 던졌으면 그대로 전달
        raise
    except Exception as e:
        print(f"🔥 get_mentor_profile_id 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"멘토 프로필 조회 실패: {str(e)}",
        )


# ----- 1. 생성 (POST) -----

@router.post("/api/availability/", status_code=status.HTTP_201_CREATED)
def create_availability_slot(slot: AvailabilityCreate):
    """
    멘토의 예약 가능 슬롯 1개 생성
    """
    try:
        mentor_profile_id = get_mentor_profile_id(slot.user_id)

        payload = {
            "mentor_id": str(mentor_profile_id),
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "is_booked": False,
        }

        response = supabase.table("mentor_availability").insert(payload).execute()

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="슬롯 생성에 실패했습니다.",
            )

        return jsonable_encoder(response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- 2. 조회 (GET) -----

@router.get("/api/availability/{user_id}")
def get_mentor_availability(user_id: uuid.UUID):
    """
    특정 멘토(user_id 기준)의 향후 예약 가능 슬롯 조회
    """
    try:
        mentor_profile_id = get_mentor_profile_id(user_id)

        response = (
            supabase.table("mentor_availability")
            .select("*")
            .eq("mentor_id", str(mentor_profile_id))
            .eq("is_booked", False)
            .gte("start_time", datetime.now().isoformat())
            .order("start_time", desc=False)
            .execute()
        )

        return jsonable_encoder(response.data or [])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- 3. 수정 (PUT) -----

@router.put("/api/availability/{slot_id}")
def update_availability_slot(slot_id: uuid.UUID, update_data: AvailabilityUpdate):
    """
    슬롯 시간(start_time / end_time) 수정
    (단순 버전: mentor_id 검증 없이 slot_id 기준으로만 수정)
    """
    try:
        update_payload = update_data.dict(exclude_unset=True)

        if not update_payload:
            raise HTTPException(
                status_code=400,
                detail="수정할 값이 없습니다.",
            )

        response = (
            supabase.table("mentor_availability")
            .update(update_payload)
            .eq("id", str(slot_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="해당 슬롯을 찾을 수 없습니다.",
            )

        return jsonable_encoder(response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- 4. 삭제 (DELETE) -----

@router.delete("/api/availability/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability_slot(slot_id: uuid.UUID):
    """
    슬롯 1개 삭제
    (단순 버전: mentor_id 검증 없이 slot_id 기준으로만 삭제)
    """
    try:
        response = (
            supabase.table("mentor_availability")
            .delete()
            .eq("id", str(slot_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="해당 슬롯을 찾을 수 없습니다.",
            )

        # 204 No Content 이므로 본문 없음
        return

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
