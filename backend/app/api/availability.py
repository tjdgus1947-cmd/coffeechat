from fastapi import APIRouter, HTTPException, Body, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from app.core.config import supabase
from .auth import get_current_user_id # ⭐️ 인증 헬퍼 임포트
from fastapi.encoders import jsonable_encoder

router = APIRouter()

# --- 스키마 정의 ---

class AvailabilityCreate(BaseModel):
    user_id: uuid.UUID  # ⭐️ auth.users.id를 받습니다. (mentor_id 대신)
    start_time: datetime
    end_time: datetime

class AvailabilityUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# --- 헬퍼 함수 ---

def get_mentor_profile_id(user_id: uuid.UUID) -> uuid.UUID:
    """auth.users.id를 사용하여 mentor_profiles.id (PK)를 찾습니다."""
    try:
        profile_res = supabase.table("mentor_profiles") \
            .select("id") \
            .eq("user_id", str(user_id)) \
            .single() \
            .execute()

        if not profile_res.data:
            raise HTTPException(status_code=404, detail="멘토 프로필을 찾을 수 없습니다.")
        
        return profile_res.data['id']
    except Exception as e:
        print(f"🔥 get_mentor_profile_id 오류: {e}")
        raise HTTPException(status_code=500, detail=f"멘토 프로필 조회 실패: {str(e)}")

# --- 1. 생성 (POST) API ---

# @router.post("/api/availability/")
# def create_availability_slot(slot: AvailabilityCreate):
#     """멘토가 '커피챗 가능한 시간' 1개를 DB에 등록합니다."""
#     try:
#         # 1. user_id로 mentor_id (PK) 찾기
#         mentor_profile_id = get_mentor_profile_id(slot.user_id)
        
#         # 2. DB에 삽입
#         response = supabase.table('mentor_availability').insert({
#             "mentor_id": str(mentor_profile_id), # ⭐️ 찾은 멘토 프로필 ID 사용
#             "start_time": slot.start_time.isoformat(),
#             "end_time": slot.end_time.isoformat(),
#             "is_booked": False
#         }).execute() # 👈 .select('*') 제거

#         # 3. .select()가 없으므로 status_code로 성공 여부 판단
#         if response.status_code < 200 or response.status_code >= 300:
#              raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create slot")
        
#         # 4. 데이터 본문 대신 성공 메시지 반환
#         return jsonable_encoder({"message": "Availability slot created successfully"})

#     except HTTPException as he:
#         raise he # 이미 HTTPException인 경우 그대로 다시 발생
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/api/availability/")
def create_availability_slot(slot: AvailabilityCreate):
    try:
        print("📥 [DEBUG] POST /api/availability/ 요청 수신")
        print("➡️ 입력 slot:", slot)
        # 만약 current_user 의존성이 있다면 그 값도 찍어라 (예: current_user_id)
        # print("➡️ current_user_id:", current_user_id)
        mentor_profile = supabase.table("mentor_profiles").select("id").eq("user_id", slot.user_id).execute()

        if not mentor_profile.data:
            raise HTTPException(status_code=404, detail="멘토 프로필이 존재하지 않습니다.")
        
        mentor_profile_id = mentor_profile.data[0]["id"]  # ✅ 실제 mentor_profiles.id 값

        start = slot.start_time
        end = slot.end_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        response = supabase.table('mentor_availability').insert({
            "mentor_id": str(mentor_profile_id),
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "is_booked": False
        }).execute()

        print("🔥 DEBUG supabase insert 결과:", response)

        if not getattr(response, "data", None):
            raise HTTPException(status_code=500, detail="Failed to create slot (no response.data)")

        return {"message": "Availability slot created successfully"}

    except Exception as e:
        import traceback
        print("❗ 예외 발생 in create_availability_slot:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- 2. 조회 (GET) API ---
@router.get("/api/availability/{user_id}")
def get_mentor_availability(user_id: uuid.UUID):
    """특정 멘토의 '예약 가능한(is_booked=False)' 미래 시점의 슬롯 목록을 반환합니다."""
    try:
        # 1. user_id로 mentor_id (PK) 찾기
        mentor_profile_id = get_mentor_profile_id(user_id)
        
        # 2. 현재 UTC 시간을 기준으로 미래 슬롯 조회
        current_utc_time = datetime.now(timezone.utc).isoformat()
        
        response = supabase.table('mentor_availability') \
            .select("*") \
            .eq('mentor_id', str(mentor_profile_id)) \
            .eq('is_booked', False) \
            .gte('start_time', current_utc_time) \
            .order('start_time', desc=False) \
            .execute()
        
        return jsonable_encoder(response.data)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# --- 3. 수정 (PUT) API ---
@router.put("/api/availability/{slot_id}") 
def update_availability_slot(
    slot_id: uuid.UUID, 
    update_data: AvailabilityUpdate,
    current_user_id: str = Depends(get_current_user_id) # ⭐️ 보안: 현재 유저 ID
):
    """현재 로그인한 멘토가 자신의 슬롯 1개를 수정합니다."""
    try:
        # 1. ⭐️ 보안: 현재 유저의 멘토 프로필 ID 조회
        mentor_profile_id = get_mentor_profile_id(uuid.UUID(current_user_id))

        update_payload = update_data.model_dump(exclude_none=True)
        
        if not update_payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
            
        response = supabase.table('mentor_availability') \
            .update(update_payload) \
            .eq("id", str(slot_id)) \
            .eq("mentor_id", str(mentor_profile_id)) \
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found or you do not have permission")
            
        return jsonable_encoder({"message": f"Slot {slot_id} updated successfully"})
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"🔥 PUT /api/availability/{slot_id} Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- 4. 삭제 (DELETE) API ---
@router.delete("/api/availability/{slot_id}")
def delete_availability_slot(
    slot_id: uuid.UUID,
    current_user_id: str = Depends(get_current_user_id) # ⭐️ 보안: 현재 유저 ID
):
    """현재 로그인한 멘토가 자신의 슬롯 1개를 삭제합니다."""
    try:
        # 1. ⭐️ 보안: 현재 유저의 멘토 프로필 ID 조회
        mentor_profile_id = get_mentor_profile_id(uuid.UUID(current_user_id))

        # 2. ⭐️ 보안: slot_id와 mentor_id가 모두 일치하는 항목 삭제
        response = supabase.table('mentor_availability') \
            .delete() \
            .eq('id', str(slot_id)) \
            .eq('mentor_id', str(mentor_profile_id)) \
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Slot not found or you do not have permission to delete it")
        
        return jsonable_encoder({"message": f"Slot {slot_id} deleted successfully"})

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))