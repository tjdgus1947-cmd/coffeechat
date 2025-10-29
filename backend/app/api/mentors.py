# backend/app/api/mentors.py

from fastapi import APIRouter, HTTPException
# 4단계에서 설정한 config.py에서 supabase 클라이언트를 가져옵니다.
from app.core.config import supabase 
import uuid # 멘티 ID를 UUID 타입으로 받기 위해 추가

router = APIRouter()

@router.get("/api/mentors/")
def get_mentor_list():
    """
    모든 멘토 목록을 조회합니다. (5단계 RLS 정책에 따라 공개됨)
    """
    try:
        response = supabase.table('mentor_profiles').select('*').execute()
        
        if response.data:
            return response.data
        return [] # 데이터가 없으면 빈 리스트 반환

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/mentors/recommended/{mentee_id}")
def get_recommended_mentors(mentee_id: str): # UUID 대신 str로 받아도 좋습니다.
    """
    AI 매칭: 멘티 ID를 기반으로 추천 멘토 목록을 반환합니다.
    (WBS 4.2 / 6단계에서 만든 SQL 함수 사용)
    """
    try:
        # 1. 먼저 멘티의 임베딩 벡터를 조회합니다.
        mentee_response = supabase.table('mentee_profiles').select('embedding').eq('id', mentee_id).single().execute()
        
        if not mentee_response.data or not mentee_response.data.get('embedding'):
            raise HTTPException(status_code=404, detail="Mentee profile or embedding not found")
        
        mentee_embedding = mentee_response.data['embedding']

        # 2. 6단계에서 만든 'match_mentors' SQL 함수를 호출합니다.
        match_response = supabase.rpc('match_mentors', {
            'query_embedding': mentee_embedding, # 멘티의 임베딩
            'match_threshold': 0.5,              # 최소 유사도 (0.0 ~ 1.0)
            'match_count': 5                     # 상위 5명 (WBS 4.2 Top-K)
        }).execute()

        if match_response.data:
            return match_response.data
        return []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))