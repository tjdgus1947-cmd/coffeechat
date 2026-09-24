# backend/app/api/mentors.py

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import supabase
from .auth import get_current_user_id

router = APIRouter()


@router.get("/api/mentors/")
def get_mentor_list(current_user_id: str = Depends(get_current_user_id)):
    """users 와 mentor_profiles 를 JOIN 해 멘토 목록을 반환한다 (로그인 필요)."""
    try:
        response = supabase.table('users') \
            .select('id, full_name, mentor_profiles(id, career_info, profile_image_url, location, verification_status)') \
            .eq('role', 'mentor') \
            .execute()
        return response.data or []

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 멘토 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="멘토 목록 조회 중 오류가 발생했습니다.")


@router.get("/api/mentors/recommended/{mentee_id}")
def get_recommended_mentors(
    mentee_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """
    멘티 임베딩과 가까운 멘토를 match_mentors(pgvector) 로 조회한다.
    경로의 mentee_id 는 하위 호환용이며, 실제로는 토큰의 사용자 기준으로 조회한다.
    """
    try:
        mentee_response = supabase.table('mentee_profiles') \
            .select('embedding') \
            .eq('user_id', current_user_id) \
            .limit(1) \
            .execute()

        if not mentee_response.data:
            raise HTTPException(status_code=404, detail="멘티 프로필을 찾을 수 없습니다.")

        mentee_embedding = mentee_response.data[0].get('embedding')
        if not mentee_embedding:
            raise HTTPException(status_code=422, detail="자기소개 임베딩이 없습니다. 자기소개를 먼저 저장해 주세요.")

        # PostgREST 가 돌려준 vector 문자열을 그대로 RPC 인자로 넘긴다
        match_response = supabase.rpc('match_mentors', {
            'query_embedding': mentee_embedding,
            'match_threshold': 0.1,
            'match_count': 50,
        }).execute()

        return match_response.data or []

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 추천 멘토 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="추천 멘토 조회 중 오류가 발생했습니다.")
