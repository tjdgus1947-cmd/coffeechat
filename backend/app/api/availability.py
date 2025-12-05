from fastapi import APIRouter, HTTPException, Body, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
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
            .execute()

        if not profile_res.data:
            raise HTTPException(status_code=404, detail="멘토 프로필을 찾을 수 없습니다.")
        
        return profile_res.data['id']
    
    except HTTPException as he:
        raise he
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


        response = supabase.table('mentor_availability').insert({
            "mentor_id": str(mentor_profile_id),
            "start_time": slot.start_time.isoformat(), # 그냥 있는 그대로 저장
            "end_time": slot.end_time.isoformat(),     # 그냥 있는 그대로 저장
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
@router.get("/api/availability/{id_param}")
def get_mentor_availability(id_param: str):
    """
    입력받은 ID가 '멘토 프로필 ID'인지 '유저 ID'인지 확인해서 처리
    """
    try:
        target_mentor_id = id_param

        # 1. 혹시 이게 User ID(로그인 ID) 인지 먼저 확인해봅니다.
        # (mentor_profiles 테이블에 user_id로 등록된 게 있는지 체크)
        profile_check = supabase.table("mentor_profiles") \
            .select("id") \
            .eq("user_id", id_param) \
            .execute()
        
        # 만약 user_id로 검색해서 결과가 나왔다면? -> 아, 이건 유저 ID구나! 멘토 ID로 바꿔주자.
        if profile_check.data:
            target_mentor_id = profile_check.data[0]['id']
            print(f"🔄 User ID({id_param})를 Mentor ID({target_mentor_id})로 변환함")
        else:
            # 결과가 없으면? -> 이미 Mentor ID 였거나, 없는 유저임. 그냥 진행.
            print(f"➡️ 변환 없이 ID({id_param}) 그대로 사용")

        # 2. 조회 시작 (target_mentor_id 사용)
        # .gte('start_time', ...) 같은 시간 필터는 테스트를 위해 일단 빼셔도 좋습니다.
        response = supabase.table('mentor_availability') \
            .select("*") \
            .eq('mentor_id', str(target_mentor_id)) \
            .order('start_time', desc=False) \
            .execute()
        
        return jsonable_encoder(response.data)

    except Exception as e:
        print(f"🔥 조회 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))    


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
    slot_id: str,  # UUID 타입 대신 str로 받아서 처리하는 게 덜 까다롭습니다
    current_user_id: str = Depends(get_current_user_id)
):
    try:
        print(f"🗑️ 슬롯 삭제 요청: slot_id={slot_id}, user_id={current_user_id}")

        # 1. 삭제를 요청한 사람이 '멘토'인지, 그리고 그 멘토의 ID가 뭔지 찾습니다.
        profile_res = supabase.table("mentor_profiles") \
            .select("id") \
            .eq("user_id", current_user_id) \
            .execute()

        if not profile_res.data:
             raise HTTPException(status_code=403, detail="멘토 프로필이 없어 삭제 권한이 없습니다.")
        
        # 진짜 멘토 ID (DB에 저장된 주인 ID)
        real_mentor_id = profile_res.data[0]['id']

        # 2. 이제 '내 ID(real_mentor_id)'이면서 '이 슬롯(slot_id)'인 것을 지웁니다.
        response = supabase.table('mentor_availability') \
            .delete() \
            .eq('id', slot_id) \
            .eq('mentor_id', real_mentor_id) \
            .execute()
        
        # Supabase는 delete시 데이터를 반환하지 않을 수도 있어서, 
        # 에러가 안 났으면 성공으로 간주하거나 response.count를 확인합니다.
        
        print("✅ 삭제 성공")
        return {"message": f"Slot {slot_id} deleted successfully"}

    except Exception as e:
        print(f"🔥 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))