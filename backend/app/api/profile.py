# backend/app/api/profile.py

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import supabase
from app.services.ml_service import generate_embedding
from .auth import get_current_user_id

router = APIRouter()

# 역할별 자기소개가 저장된 테이블/컬럼
INTRO_COLUMN = {
    "mentor": ("mentor_profiles", "career_info"),
    "mentee": ("mentee_profiles", "current_situation"),
}


class ProfileUpdateRequest(BaseModel):
    role: Literal["mentor", "mentee"]
    introduction_text: str
    # 하위 호환용. 사용하지 않는다 (수정 대상은 토큰의 사용자)
    user_id: Optional[str] = None


@router.get("/api/profile/introduction")
def get_profile_introduction(
    role: Literal["mentor", "mentee"],
    user_id: Optional[str] = None,  # 하위 호환용, 사용하지 않음
    current_user_id: str = Depends(get_current_user_id),
):
    """로그인한 사용자의 자기소개를 반환한다."""
    table_name, column_name = INTRO_COLUMN[role]
    try:
        response = supabase.table(table_name) \
            .select(column_name) \
            .eq("user_id", current_user_id) \
            .limit(1) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {"introduction_text": response.data[0].get(column_name)}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 자기소개 로드 실패: {e}")
        raise HTTPException(status_code=500, detail="자기소개 조회 중 오류가 발생했습니다.")


@router.post("/api/profile/update-introduction")
def update_profile_introduction(
    request: ProfileUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    """
    자기소개 텍스트와 임베딩을 함께 갱신한다.
    텍스트만 바뀌고 임베딩이 옛 값으로 남으면 매칭 결과가 실제 소개와 어긋나므로 한 번의 UPDATE 로 같이 저장한다.
    """
    table_name, column_name = INTRO_COLUMN[request.role]
    text = request.introduction_text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="자기소개가 비어 있습니다.")

    try:
        new_embedding = generate_embedding(text)

        response = supabase.table(table_name) \
            .update({column_name: text, "embedding": new_embedding}) \
            .eq("user_id", current_user_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {"message": "프로필 및 임베딩 업데이트 성공"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 프로필 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail="프로필 업데이트 중 오류가 발생했습니다.")
