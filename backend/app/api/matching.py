# backend/app/api/matching.py
# (ERD v2 - .select() 버그 최종 수정본)

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.core.config import supabase
from app.services.ml_service import generate_embedding
import uuid

router = APIRouter()

class EmbeddingRequest(BaseModel):
    user_id: uuid.UUID # public.users.id
    role: str      # 'mentor' 또는 'mentee'
    text_data: str # 멘토의 'career_info' 또는 멘티의 'career_goal'

@router.post("/api/matching/generate-embedding")
def create_embedding_and_update(request: EmbeddingRequest):
    """
    (수정됨) 텍스트 데이터를 AI 임베딩으로 변환하고,
    'user_id'를 기준으로 해당 프로필 테이블(DB)을 업데이트합니다.
    """
    try:
        embedding = generate_embedding(request.text_data)
        
        table_name = ""
        if request.role == 'mentor':
            table_name = 'mentor_profiles'
        elif request.role == 'mentee':
            table_name = 'mentee_profiles'
        else:
            raise HTTPException(status_code=400, detail="Invalid role")

        # 🚨 (수정된 핵심 로직)
        # .update() 뒤의 .select()를 제거하고,
        # response.count를 확인하여 성공 여부를 판단합니다.
        response = supabase.table(table_name) \
                           .update({"embedding": embedding}) \
                           .eq("user_id", str(request.user_id)) \
                           .execute()
        
        # (수정) .execute()는 업데이트된 행의 'count'를 반환합니다.
        if response.count == 0:
             raise HTTPException(status_code=404, detail="404: User profile not found or update failed")

        return {"message": f"{request.role} {request.user_id}의 임베딩이 생성/업데이트되었습니다."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))