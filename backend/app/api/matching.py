# backend/app/api/matching.py

from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from app.core.config import supabase
from app.services.ml_service import generate_embedding
from app.services.matching_service import (
    calculate_final_match_score,
    extract_coordinates_from_geography
)
import uuid
import unicodedata
import json
import logging # ⭐️ [추가] 로깅 라이브러리 임포트
from typing import List, Dict # ⭐️ [추가] 타이핑 임포트

# ⭐️ [추가] 로거 설정
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

# ⭐️ [추가] location.py에서 페이지네이션 헬퍼 함수 복사
def fetch_all_with_pagination(table_name: str, select_query: str, chunk_size: int = 1000) -> List[dict]:
    """
    Supabase에서 데이터를 페이지네이션으로 모두 가져옵니다.
    (WinError 10035 소켓 오류 해결용)
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

# --- (임베딩/위치 업데이트 API - 기존과 동일) ---

@router.post("/api/matching/generate-embedding")
def create_embedding_and_update(request: EmbeddingRequest):
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

# --- (⭐️⭐️⭐️ 핵심 수정 API ⭐️⭐️⭐️) ---

@router.get("/api/matching/find-matches")
def find_matches_with_location(
    user_id: str = Query(..., description="현재 사용자 ID"),
    role: str = Query(..., description="'mentor' 또는 'mentee'"),
    # ⭐️ [수정] 422 오류 해결: le=50 -> le=100 (프론트엔드 요청에 맞춤)
    limit: int = Query(10, ge=1, le=100, description="반환할 최대 매칭 수"),
    max_distance: float = Query(50.0, ge=1, description="최대 거리 기준 (km)")
):
    try:
        user_id_str = get_clean_user_id(user_id)
        current_table = 'mentee_profiles' if role == 'mentee' else 'mentor_profiles'
        target_table = 'mentor_profiles' if role == 'mentee' else 'mentee_profiles'

        # ⭐️ [수정] 500 오류 해결: 페이지네이션으로 현재 사용자 정보 가져오기
        all_current_profiles_data = fetch_all_with_pagination(
            current_table, "user_id, embedding, location"
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
        
        # ⭐️ [수정] 500 오류 해결: 페이지네이션으로 모든 매칭 후보 가져오기 (인라인 루프)
        all_candidates_data = []
        offset = 0
        chunk_size = 1000 # 한 번에 1000명씩
        
        while True:
            logger.info(f"Fetching candidates from {target_table}: {offset} to {offset + chunk_size - 1}...")
            candidates_response = supabase.table(target_table) \
                                          .select("user_id, embedding, location") \
                                          .not_.is_("embedding", "null") \
                                          .not_.is_("location", "null") \
                                          .range(offset, offset + chunk_size - 1) \
                                          .execute()
            
            if candidates_response.data:
                all_candidates_data.extend(candidates_response.data)
                if len(candidates_response.data) < chunk_size:
                    break # 마지막 페이지
                offset += chunk_size
            else:
                break # 데이터 없음
        
        logger.info(f"Total candidates fetched: {len(all_candidates_data)}")

        matches = []
        # ⭐️ [수정] candidates_response.data -> all_candidates_data
        for candidate in all_candidates_data:
            if candidate.get('user_id') and get_clean_user_id(candidate['user_id']) == user_id_str:
                continue # 자기 자신 제외
            
            try:
                candidate_lat, candidate_lon = extract_coordinates_from_geography(candidate['location'])
                candidate_embedding = json.loads(candidate['embedding'])
                
                match_result = calculate_final_match_score(
                    current_embedding,
                    candidate_embedding,
                    current_lat, current_lon,
                    candidate_lat, candidate_lon,
                    max_distance=max_distance
                )
                
                matches.append({
                    "user_id": candidate['user_id'],
                    "final_score": match_result['final_score'],
                    "text_similarity": match_result['text_similarity'],
                    "distance_km": match_result['distance_km'],
                    "distance_score": match_result['distance_score'],
                    "breakdown": match_result['breakdown']
                })
            except Exception as e:
                logger.warning(f"Failed to process candidate {candidate.get('user_id')}: {e}")
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


@router.get("/api/matching/debug/{user_id}")
def debug_user_profile(
    user_id: str, 
    role: str = Query(...)
):
    try:
        user_id_str = get_clean_user_id(user_id)
        table_name = 'mentor_profiles' if role == 'mentor' else 'mentee_profiles'

        # ⭐️ [수정] 디버그 API도 페이지네이션 적용
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
        raise HTTPException(status_code=500, detail=str(e))