from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from app.core.config import supabase
from app.services.ml_service import generate_embedding
from app.services.matching_service import (
    calculate_final_match_score,
    extract_coordinates_from_geography
)
from app.services.reranking_service import rerank_candidates
from app.services.feedback_service import personalize_match_scores
from app.services.hybrid_search_service import hybrid_search, adaptive_hybrid_weights
import uuid
import unicodedata
import json
import logging
import numpy as np  # ⭐️ [추가] 벡터 연산을 위해 numpy 추가
from typing import List, Dict

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# --- (Pydantic 모델 - 기존과 동일) ---
class EmbeddingRequest(BaseModel):
    user_id: str
    role: str
    text_data: str

class LocationMatchRequest(BaseModel):
    user_id: str
    role: str
    latitude: float
    longitude: float

# --- (공통 함수 - 기존과 동일) ---
def get_clean_user_id(user_id: str) -> str:
    if not user_id: return None
    return unicodedata.normalize('NFC', user_id).strip()

def find_profile_in_list(response_data: list, user_id_str: str):
    if not response_data: return None
    for profile in response_data:
        db_user_id = profile.get('user_id')
        if db_user_id:
            db_id_clean = get_clean_user_id(db_user_id)
            if db_id_clean == user_id_str:
                return profile
    return None

def fetch_all_with_pagination(table_name: str, select_query: str, chunk_size: int = 1000) -> List[dict]:
    """
    Supabase에서 데이터를 페이지네이션으로 모두 가져옵니다.
    """
    all_data = []
    offset = 0
    while True:
        try:
            logger.info(f"Fetching {table_name}: {offset} to {offset + chunk_size - 1}...")
            response = supabase.table(table_name) \
                             .select(select_query) \
                             .range(offset, offset + chunk_size - 1) \
                             .execute()
            
            if response.data:
                all_data.extend(response.data)
                if len(response.data) < chunk_size:
                    logger.info(f"Finished fetching {table_name}. Total: {len(all_data)}")
                    break
                offset += chunk_size
            else:
                logger.info(f"Finished fetching {table_name}. Total: {len(all_data)}")
                break
        except Exception as e:
            logger.error(f"Error fetching {table_name} at offset {offset}: {e}")
            raise e 
            
    return all_data

# ⭐️ [추가] 순수 벡터 유사도 계산 헬퍼 함수
def calculate_cosine_similarity(vec_a, vec_b):
    """
    두 벡터 간의 코사인 유사도를 계산합니다 (1.0 = 완전 일치, -1.0 = 완전 반대)
    """
    try:
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)
    except Exception as e:
        logger.error(f"Vector calculation error: {e}")
        return 0.0

# --- (기존 API 엔드포인트들 생략 없이 유지) ---
@router.post("/api/matching/generate-embedding")
def create_embedding_and_update(request: EmbeddingRequest):
    # (기존 코드와 동일)
    try:
        user_id_str = get_clean_user_id(request.user_id)
        if not user_id_str: raise HTTPException(status_code=400, detail="Invalid User ID")
        table_name = 'mentor_profiles' if request.role == 'mentor' else 'mentee_profiles'
        
        embedding = generate_embedding(request.text_data) 
        
        response = supabase.table(table_name) \
                           .update({"embedding": embedding}) \
                           .eq("user_id", user_id_str) \
                           .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found for embedding update")
        
        return {"message": f"{request.role} {user_id_str}의 임베딩이 생성되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/matching/update-location")
def update_user_location(request: LocationMatchRequest):
    # (기존 코드와 동일)
    try:
        user_id_str = get_clean_user_id(request.user_id)
        if not user_id_str: raise HTTPException(status_code=400, detail="Invalid User ID")

        table_name = 'mentor_profiles' if request.role == 'mentor' else 'mentee_profiles'
        geography_point = f"POINT({request.longitude} {request.latitude})"
        
        response = supabase.table(table_name) \
                           .update({"location": geography_point}) \
                           .eq("user_id", user_id_str) \
                           .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found for location update")
        
        return {"message": "위치 정보가 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/matching/find-matches")
def find_matches_with_location(
    user_id: str = Query(..., description="현재 사용자 ID"),
    role: str = Query(..., description="'mentor' 또는 'mentee'"),
    limit: int = Query(10, ge=1, le=100, description="반환할 최대 매칭 수"),
    max_distance: float = Query(50.0, ge=1, description="최대 거리 기준 (km)")
):
    # (기존 코드와 동일 - 멘티용 매칭 로직)
    try:
        user_id_str = get_clean_user_id(user_id)
        current_table = 'mentee_profiles' if role == 'mentee' else 'mentor_profiles'
        target_table = 'mentor_profiles' if role == 'mentee' else 'mentee_profiles'
        
        # Define text columns and keyword boost based on role
        current_text_column = 'interest' if role == 'mentee' else 'career_info'
        target_text_column = 'career_info' if role == 'mentee' else 'interest'
        keyword_boost = 0.15

        all_current_profiles_data = fetch_all_with_pagination(
            current_table, "user_id, embedding, location, " + current_text_column
        )
        current_profile = find_profile_in_list(all_current_profiles_data, user_id_str)
        
        if current_profile is None:
            raise HTTPException(status_code=404, detail="User profile not found (Python search failed)")
        
        if not current_profile.get('embedding'):
            raise HTTPException(status_code=400, detail="임베딩이 생성되지 않았습니다.")
        if not current_profile.get('location'):
            raise HTTPException(status_code=400, detail="위치 정보가 없습니다.")
        
        current_embedding = json.loads(current_profile['embedding'])
        current_lat, current_lon = extract_coordinates_from_geography(current_profile['location'])
        current_text = current_profile.get(current_text_column, "")
        
        # 1️⃣ 1차 매칭 (기본 임베딩 + 거리)
        logger.info("📍 1단계: 기본 매칭 시작")
        
        all_candidates_data = fetch_all_with_pagination(
            target_table, "user_id, embedding, location, " + target_text_column
        )
        
        matches = []
        for candidate in all_candidates_data:
            if candidate.get('user_id') and get_clean_user_id(candidate['user_id']) == user_id_str:
                continue 
            
            try:
                candidate_lat, candidate_lon = extract_coordinates_from_geography(candidate['location'])
                candidate_embedding = json.loads(candidate['embedding'])
                candidate_text = candidate.get(target_text_column, "")
                
                match_result = calculate_final_match_score(
                    current_embedding,
                    candidate_embedding,
                    current_lat, current_lon,
                    candidate_lat, candidate_lon,
                    text1=current_text,
                    text2=candidate_text,
                    max_distance=max_distance,
                    keyword_boost=keyword_boost
                )
                
                matches.append({
                    "user_id": candidate['user_id'],
                    "text": candidate_text,  # 🔥 Re-ranking/하이브리드용
                    "embedding": candidate_embedding,  # 🔥 하이브리드용
                    "final_score": match_result['final_score'],
                    "text_similarity": match_result['text_similarity'],
                    "distance_km": match_result['distance_km'],
                    "distance_score": match_result['distance_score'],
                    "breakdown": match_result['breakdown']
                })
            except Exception as e:
                logger.warning(f"후보 처리 실패: {e}")
                continue
        
        matches.sort(key=lambda x: x['final_score'], reverse=True)
        return {"user_id": user_id, "matches": matches[:limit]}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔥 Find Matches Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ⭐️ [추가] 멘토-멘토 네트워크 전용 API (100% 벡터 유사도)
@router.get("/api/matching/mentor-network")
def find_mentor_network_matches(
    user_id: str = Query(..., description="현재 멘토의 User ID"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 유사 멘토 수"),
    min_similarity: float = Query(0.0, ge=0.0, le=1.0, description="최소 유사도 임계값")
):
    """
    멘토-멘토 간의 네트워크 형성을 위해, 오직 '임베딩 유사도(Cosine Similarity)'만을 기준으로
    유사한 멘토들을 찾습니다. (위치 정보 배제)
    """
    try:
        user_id_str = get_clean_user_id(user_id)
        
        # 1. 모든 멘토 프로필 조회 (DB 구조상 mentor_profiles 테이블 사용)
        # 네트워크 그래프에 필요한 정보(이름 등)를 위해 필요한 컬럼을 선택
        all_mentors_data = fetch_all_with_pagination(
            "mentor_profiles", 
            "user_id, embedding, career_info"  # users 테이블 조인은 프론트엔드나 별도 쿼리로 처리 가정
        )
        
        # 2. 내 프로필 찾기
        my_profile = find_profile_in_list(all_mentors_data, user_id_str)
        
        if my_profile is None:
            raise HTTPException(status_code=404, detail="Current mentor profile not found")
            
        if not my_profile.get('embedding'):
            raise HTTPException(status_code=400, detail="Current mentor has no embedding data")
            
        my_embedding = np.array(json.loads(my_profile['embedding']))
        
        network_matches = []
        
        # 3. 다른 멘토들과 유사도 계산 (Loop)
        for other in all_mentors_data:
            other_user_id = other.get('user_id')
            if not other_user_id: continue
            
            # 자기 자신 제외
            if get_clean_user_id(other_user_id) == user_id_str:
                continue
                
            try:
                if not other.get('embedding'): continue
                
                other_embedding = np.array(json.loads(other['embedding']))
                
                # 순수 벡터 코사인 유사도 계산
                similarity = calculate_cosine_similarity(my_embedding, other_embedding)
                
                # 최소 임계값 필터링
                if similarity < min_similarity:
                    continue
                
                network_matches.append({
                    "user_id": other_user_id,
                    "similarity": float(similarity), # numpy float -> python float 변환
                    "career_info": other.get('career_info')
                })
                
            except Exception as e:
                logger.warning(f"Error calculating similarity for mentor {other_user_id}: {e}")
                continue
                
        # 4. 유사도 순으로 정렬 (내림차순)
        network_matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            "center_user_id": user_id_str,
            "matches": network_matches[:limit]
        }

    except Exception as e:
        logger.error(f"🔥 Mentor Network Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/matching/debug/{user_id}")
def debug_user_profile(user_id: str, role: str = Query(...)):
    # (기존 디버그 코드 유지)
    try:
        user_id_str = get_clean_user_id(user_id)
        table_name = 'mentor_profiles' if role == 'mentor' else 'mentee_profiles'

        all_profiles_data = fetch_all_with_pagination(
            table_name, "user_id, embedding, location"
        )
        profile = find_profile_in_list(all_profiles_data, user_id_str)
        
        if profile is None:
            raise HTTPException(status_code=404, detail="User not found (Python search failed)")

        embedding_list = None
        embedding_dim = 0
        embedding_error = None

        try:
            if profile.get('embedding'):
                embedding_list = json.loads(profile['embedding'])
                embedding_dim = len(embedding_list)
        except Exception as e:
            embedding_error = f"Failed to parse embedding string: {e}"

        result = {
            "user_id": profile['user_id'],
            "has_embedding": embedding_list is not None,
            "embedding_dimension": embedding_dim,
            "embedding_parse_error": embedding_error,
            "has_location": profile.get('location') is not None,
            "location_raw": profile.get('location')
        }
        
        if profile.get('location'):
            try:
                lat, lon = extract_coordinates_from_geography(profile['location'])
                result['location_parsed'] = {"latitude": lat, "longitude": lon}
            except Exception as e:
                result['location_error'] = str(e)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"고급 매칭 실패: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))