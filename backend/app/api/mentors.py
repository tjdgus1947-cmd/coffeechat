# backend/app/api/mentors.py
# (ERD v2 - AI 매칭 임계값 수정)

from fastapi import APIRouter, HTTPException
from app.core.config import supabase
import uuid

router = APIRouter()

@router.get("/api/mentors/")
def get_mentor_list():
    """
    (수정됨) 새로운 ERD에 맞춰 public.users[cite: setup_v2.sql]와 mentor_profiles[cite: setup_v2.sql]를 JOIN하여
    모든 멘토 목록을 조회합니다.
    """
    try:
        response = supabase.table('users') \
                           .select('id, full_name, mentor_profiles(id, career_info, profile_image_url, location, verification_status)') \
                           .eq('role', 'mentor') \
                           .execute()
        
        if response.data:
            return response.data
        return []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/mentors/recommended/{mentee_id}")
def get_recommended_mentors(mentee_id: str):
    """
    AI 매칭: 멘티 ID를 기반으로 추천 멘토 목록을 반환합니다.
    (IndexError 버그 수정)
    """
    try:
        print(f"AI 추천 API 수신: 멘티 ID {mentee_id}") 

        # 1. 멘티의 임베딩 벡터 조회
        mentee_response = supabase.table('mentee_profiles') \
                                  .select('embedding') \
                                  .eq('user_id', mentee_id) \
                                  .limit(1) \
                                  .execute()
        
        if not mentee_response.data:
            print(f"오류: 멘티 프로필을 찾을 수 없습니다 (ID: {mentee_id})")
            raise HTTPException(status_code=404, detail=f"Mentee profile not found for this user_id: {mentee_id}")
        
        mentee_profile = mentee_response.data[0]
        
        if not mentee_profile.get('embedding'):
            print(f"오류: 멘티 임베딩이 NULL입니다 (ID: {mentee_id})")
            raise HTTPException(status_code=404, detail="Mentee embedding is NULL. Please generate embedding first.")
        
        mentee_embedding = mentee_profile['embedding']
        print(f"멘티 임베딩 로드 성공 (ID: {mentee_id})")

        # 2. 'match_mentors' SQL 함수 호출
        # 🚨 (수정) 임계값을 0.5에서 0.1로 낮춤
        match_response = supabase.rpc('match_mentors', {
            'query_embedding': mentee_embedding,
            'match_threshold': 0.1, # 👈 50% -> 10%
            'match_count': 5 
        }).execute()

        if match_response.data:
            print(f"AI 매칭 성공: {len(match_response.data)}명의 멘토 반환")
            return match_response.data
        
        print("AI 매칭 결과: 추천할 멘토 없음 (빈 배열 반환)")
        return []

    except Exception as e:
        print(f"심각한 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))