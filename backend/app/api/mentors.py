# backend/app/api/mentors.py
# (ERD v2 - AI 매칭 + 거리 기반 점수 계산)

from fastapi import APIRouter, HTTPException
from app.core.config import supabase
from app.services.ml_service import calculate_distance_score, calculate_final_score
from app.api.location import parse_location
import uuid
import re

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
    AI 매칭: 멘티 ID를 기반으로 텍스트 유사도(70%) + 거리(30%) 점수를 계산하여 추천 멘토 목록을 반환합니다.
    """
    try:
        print(f"✅ AI 추천 API 수신: 멘티 ID {mentee_id}") 

        # 1. 멘티 프로필 조회 (임베딩 + 위치)
        mentee_response = supabase.table('mentee_profiles') \
                                  .select('embedding, location') \
                                  .eq('user_id', mentee_id) \
                                  .limit(1) \
                                  .execute()
        
        if not mentee_response.data:
            raise HTTPException(status_code=404, detail=f"Mentee profile not found: {mentee_id}")
        
        mentee_profile = mentee_response.data[0]
        mentee_embedding = mentee_profile.get('embedding')
        mentee_location_data = mentee_profile.get('location')
        
        if not mentee_embedding:
            raise HTTPException(status_code=404, detail="Mentee embedding is NULL")
        
        mentee_location = parse_location(mentee_location_data) if mentee_location_data else None
        mentee_lon, mentee_lat = mentee_location if mentee_location else (None, None)
        print(f"📍 멘티 위치: lat={mentee_lat}, lon={mentee_lon}")

        # 2. 텍스트 유사도 기반 멘토 검색
        match_response = supabase.rpc('match_mentors', {
            'query_embedding': mentee_embedding,
            'match_threshold': 0.01,
            'match_count': 20
        }).execute()

        if not match_response.data:
            print("⚠️ 추천 멘토 없음")
            return []
        
        raw_mentors = match_response.data
        print(f"📊 {len(raw_mentors)}명의 멘토 검색됨")

        # 3. 각 멘토에 대해 거리 계산 및 최종 점수 산출
        enriched_mentors = []
        has_location_data = mentee_lat is not None and mentee_lon is not None
        
        for mentor in raw_mentors:
            mentor_location_data = mentor.get('location')
            mentor_location = parse_location(mentor_location_data) if mentor_location_data else None
            mentor_lon, mentor_lat = mentor_location if mentor_location else (None, None)
            
            # 거리 계산
            distance_km, distance_score = calculate_distance_score(
                mentee_lat, mentee_lon,
                mentor_lat, mentor_lon
            )
            
            # 텍스트 유사도 (0~1 스케일)
            text_similarity = mentor.get('similarity', 0)
            
            # 최종 점수 계산
            # 위치 데이터가 없으면 텍스트 유사도만 100% 사용
            if not has_location_data or distance_score is None:
                final_score = text_similarity * 100  # 텍스트 유사도를 그대로 사용
            else:
                # 위치 데이터가 있으면 가중치 적용 (텍스트 70% + 거리 30%)
                final_score = calculate_final_score(text_similarity, distance_score)
            
            enriched_mentors.append({
                'id': mentor.get('id'),
                'user_id': mentor.get('user_id'),
                'full_name': mentor.get('full_name'),
                'career_info': mentor.get('career_info'),
                'profile_image_url': mentor.get('profile_image_url'),
                'similarity': text_similarity,  # 원본 유사도 (호환성)
                'text_similarity': text_similarity,  # 텍스트 유사도
                'distance_km': distance_km,
                'distance_score': distance_score if distance_score else 0,
                'final_score': final_score
            })
        
        # 최종 점수로 정렬
        enriched_mentors.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 상위 20명만 반환
        top_mentors = enriched_mentors[:20]

        print(f"🎯 최종 추천: {len(top_mentors)}명")
        for m in top_mentors:
            print(f"  - {m['full_name']}: 최종={m['final_score']}% (텍스트={m['text_similarity']*100:.1f}%, 거리={m['distance_km']}km)")

        return top_mentors

    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))