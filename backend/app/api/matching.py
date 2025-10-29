# backend/app/api/matching.py

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
# 4단계에서 설정한 config.py에서 supabase 클라이언트를 가져옵니다.
from app.core.config import supabase
# 15.2에서 만든 AI 임베딩 생성 함수를 가져옵니다.
from app.services.ml_service import generate_embedding

router = APIRouter()

class EmbeddingRequest(BaseModel):
    user_id: str # 멘토 또는 멘티의 UUID
    role: str      # 'mentor' 또는 'mentee'
    text_data: str # 멘토의 'career_info' 또는 멘티의 'career_goal'

@router.post("/api/matching/generate-embedding")
def create_embedding_and_update(request: EmbeddingRequest):
    """
    텍스트 데이터를 받아 AI 임베딩을 생성하고,
    해당 유저의 프로필 테이블(DB)을 업데이트합니다. (WBS 4.1)
    """
    try:
        # 1. 텍스트 데이터를 AI 임베딩 벡터로 변환
        embedding = generate_embedding(request.text_data)

        table_name = ""
        if request.role == 'mentor':
            table_name = 'mentor_profiles'
        elif request.role == 'mentee':
            table_name = 'mentee_profiles'
        else:
            raise HTTPException(status_code=400, detail="Invalid role")

        # 2. Supabase DB의 'embedding' 컬럼을 업데이트(UPDATE)
        response = supabase.table(table_name)\
                           .update({"embedding": embedding})\
                           .eq("id", request.user_id)\
                           .execute()

        if not response.data:
             raise HTTPException(status_code=404, detail="User profile not found or update failed")

        return {"message": f"{request.role} {request.user_id}의 임베딩이 생성/업데이트되었습니다."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))