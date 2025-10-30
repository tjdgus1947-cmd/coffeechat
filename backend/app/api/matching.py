from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import uuid
from app.core.config import supabase
from app.services.ml_service import generate_embedding # AI 모델

router = APIRouter()

class EmbeddingRequest(BaseModel):
    user_id: str # 멘토 또는 멘티의 UUID
    role: str
    text_data: str

@router.post("/api/matching/generate-embedding")
def create_embedding_and_update(request: EmbeddingRequest):
    """
    [WBS 4.1] 텍스트를 AI 임베딩 벡터로 변환하고 DB를 업데이트합니다.
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
        #    (에러 유발하는 .select() 제거)
        response = supabase.table(table_name)\
                           .update({"embedding": embedding})\
                           .eq("id", request.user_id)\
                           .execute() 
        
        # 3. 업데이트가 성공적으로 실행되었는지 확인 (업데이트된 행의 개수가 0개면 실패)
        if response.count == 0:
             # 이 에러는 ID가 DB에 없거나, ID는 있지만 RLS에 막혔을 때 발생합니다.
             # RLS는 백엔드에서 'service_role'로 접근하기 때문에 ID 오류가 확실합니다.
             raise HTTPException(status_code=404, detail="404: User profile not found (ID is incorrect or deleted)")

        return {"message": f"{request.role} {request.user_id}의 임베딩이 생성/업데이트되었습니다."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error during embedding: {str(e)}")