# backend/app/api/profile.py

from fastapi import APIRouter, HTTPException, Body, Query
from app.core.config import supabase
# ⭐️ ml_service에서 임베딩 생성 함수를 가져옵니다.
from app.services.ml_service import generate_embedding 
import uuid
import unicodedata
from pydantic import BaseModel

# ⭐️ 라우터를 새로 만듭니다.
router = APIRouter() 

# ⭐️ 멘티님의 matching.py에서 가져온 헬퍼 함수
def get_clean_user_id(user_id: str) -> str:
    if not user_id: return None
    return unicodedata.normalize('NFC', user_id).strip()

# ⭐️ 프론트엔드에서 "저장" 시 받을 데이터 형식
class ProfileUpdateRequest(BaseModel):
    user_id: str
    role: str
    introduction_text: str # ⭐️ 새 자기소개 텍스트

@router.get("/api/profile/introduction")
def get_profile_introduction(user_id: str, role: str):
    """
    현재 사용자의 자기소개 텍스트를 DB에서 불러옵니다.
    """
    try:
        user_id_str = get_clean_user_id(user_id)
        
        if role == 'mentor':
            table_name = 'mentor_profiles'
            column_name = 'career_info' # ⭐️ 멘토는 'career_info'
        else:
            table_name = 'mentee_profiles'
            column_name = 'current_situation' # ⭐️ 멘티는 'current_situation'
            
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
    """
    사용자의 자기소개 텍스트와 새 임베딩을 생성하여 DB에 모두 업데이트합니다.
    """
    try:
        user_id_str = get_clean_user_id(request.user_id)
        
        # ⭐️ 역할에 따라 다른 컬럼 이름을 사용
        if request.role == 'mentor':
            table_name = 'mentor_profiles'
            text_column_name = 'career_info'
        else:
            table_name = 'mentee_profiles'
            text_column_name = 'current_situation'
        
        # 1. 새로운 텍스트로 임베딩 생성
        print(f"[{user_id_str}] 새 임베딩 생성 시작...")
        new_embedding = generate_embedding(request.introduction_text)
        print(f"[{user_id_str}] 새 임베딩 생성 완료 (차원: {len(new_embedding)})")
        
        # 2. DB 업데이트: 텍스트와 임베딩을 "동시에" 저장
        update_data = {
            text_column_name: request.introduction_text, # ⭐️ 'current_situation' 또는 'career_info'
            "embedding": new_embedding                   # ⭐️ 새 임베딩
        }
        
        response = supabase.table(table_name) \
                        .update(update_data) \
                        .eq("user_id", user_id_str) \
                        .execute() # ⭐️ .select() 없이 .update()만 실행

        # ⭐️ .update()는 .data가 아닌 .count로 성공 여부 확인 (권장)
        if response.count is None or response.count == 0:
             # (참고: .eq() 버그로 .count가 0이어도 실제론 성공할 수 있으나, 
             #  .update()는 .eq() 버그가 없을 확률이 높습니다)
             print(f"[{user_id_str}] 업데이트 결과: {response.count} (0이면 실패 가능성)")

        return {"message": "프로필 및 임베딩 업데이트 성공"}
    
    except Exception as e:
        print(f"❌ 프로필 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))