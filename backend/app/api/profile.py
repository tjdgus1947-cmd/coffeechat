from fastapi import APIRouter, HTTPException, Body
from app.core.config import supabase
from app.services.ml_service import generate_embedding
import unicodedata
from pydantic import BaseModel

router = APIRouter()

def get_clean_user_id(user_id: str) -> str:
    if not user_id: return None
    return unicodedata.normalize('NFC', user_id).strip()

class ProfileUpdateRequest(BaseModel):
    user_id: str
    role: str
    introduction_text: str

@router.get("/api/profile/introduction")
def get_profile_introduction(user_id: str, role: str):
    try:
        user_id_str = get_clean_user_id(user_id)
        if role == 'mentor':
            table_name = 'mentor_profiles'
            column_name = 'career_info'
        else:
            table_name = 'mentee_profiles'
            column_name = 'current_situation'
        response = supabase.table(table_name) \
                            .select(column_name) \
                            .eq("user_id", user_id_str) \
                            .limit(1) \
                            .execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"introduction_text": response.data[0].get(column_name)}
    except Exception as e:
        print(f"❌ 자기소개 로드 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/profile/update-introduction")
def update_profile_introduction(request: ProfileUpdateRequest):
    try:
        user_id_str = get_clean_user_id(request.user_id)
        if request.role == 'mentor':
            table_name = 'mentor_profiles'
            text_column_name = 'career_info'
        else:
            table_name = 'mentee_profiles'
            text_column_name = 'current_situation'
        new_embedding = generate_embedding(request.introduction_text)
        update_data = {
            text_column_name: request.introduction_text,
            "embedding": new_embedding
        }
        response = supabase.table(table_name) \
                        .update(update_data) \
                        .eq("user_id", user_id_str) \
                        .execute()
        if response.count is None or response.count == 0:
            print(f"[update] 결과: {response.count} (0이면 실패 가능성)")
        return {"message": "프로필 및 임베딩 업데이트 성공"}
    except Exception as e:
        print(f"❌ 프로필 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
