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
import json  # ⭐️⭐️⭐️ 1. json 라이브러리를 임포트합니다. ⭐️⭐️⭐️

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

# --- (임베딩/위치 업데이트 API - 기존과 동일) ---

@router.post("/api/matching/generate-embedding")
def create_embedding_and_update(request: EmbeddingRequest):
    try:
        user_id_str = get_clean_user_id(request.user_id)
        if not user_id_str: raise HTTPException(status_code=400, detail="Invalid User ID")
        table_name = 'mentor_profiles' if request.role == 'mentor' else 'mentee_profiles'
        
        # ⭐️ ml_service.py가 list[float]를 반환 (정상)
        embedding = generate_embedding(request.text_data) 
        
        response = supabase.table(table_name) \
                            .update({"embedding": embedding}) \
                            .eq("user_id", user_id_str) \
                            .select("user_id") \
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
                            .select("user_id") \
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
    limit: int = Query(10, ge=1, le=50, description="반환할 최대 매칭 수"),
    max_distance: float = Query(50.0, ge=1, description="최대 거리 기준 (km)")
):
    try:
        user_id_str = get_clean_user_id(user_id)
        current_table = 'mentee_profiles' if role == 'mentee' else 'mentor_profiles'
        target_table = 'mentor_profiles' if role == 'mentee' else 'mentee_profiles'

        # 1. 현재 사용자 정보 가져오기 (WKB)
        all_current_profiles_response = supabase.table(current_table) \
                                                .select("user_id, embedding, location") \
                                                .execute()

        current_profile = find_profile_in_list(all_current_profiles_response.data, user_id_str)
        
        if current_profile is None:
            raise HTTPException(status_code=404, detail="User profile not found (Python search failed)")
        
        if not current_profile.get('embedding'):
            raise HTTPException(status_code=400, detail="임베딩이 생성되지 않았습니다.")
        if not current_profile.get('location'):
            raise HTTPException(status_code=400, detail="위치 정보가 없습니다.")
        
        # ⭐️ 2. 임베딩(str)을 list[float]로 변환 ⭐️
        current_embedding = json.loads(current_profile['embedding'])
        current_lat, current_lon = extract_coordinates_from_geography(current_profile['location'])
        
        # 3. 모든 매칭 후보 가져오기 (WKB)
        candidates_response = supabase.table(target_table) \
                                        .select("user_id, embedding, location") \
                                        .not_.is_("embedding", "null") \
                                        .not_.is_("location", "null") \
                                        .execute()
        
        matches = []
        for candidate in candidates_response.data:
            if candidate.get('user_id') and get_clean_user_id(candidate['user_id']) == user_id_str:
                continue # 자기 자신 제외
            
            try:
                candidate_lat, candidate_lon = extract_coordinates_from_geography(candidate['location'])
                
                # ⭐️ 4. 후보자 임베딩(str)도 list[float]로 변환 ⭐️
                candidate_embedding = json.loads(candidate['embedding'])
                
                match_result = calculate_final_match_score(
                    current_embedding, # 이제 list[float]
                    candidate_embedding, # 이제 list[float]
                    current_lat, current_lon,
                    candidate_lat, candidate_lon,
                    max_distance=max_distance
                )
                
                matches.append({
                    "user_id": candidate['user_id'],
                    "final_score": match_result['final_score'],
                    # (이하 생략 - 기존 코드와 동일)
                    "text_similarity": match_result['text_similarity'],
                    "distance_km": match_result['distance_km'],
                    "distance_score": match_result['distance_score'],
                    "breakdown": match_result['breakdown']
                })
            except Exception as e:
                # ⭐️ json.loads 실패 또는 calculate_match_score 실패 시 스킵
                print(f"Failed to process candidate {candidate.get('user_id')}: {e}")
                continue
        
        matches.sort(key=lambda x: x['final_score'], reverse=True)
        return {"user_id": user_id, "matches": matches[:limit]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/matching/debug/{user_id}")
def debug_user_profile(
    user_id: str, 
    role: str = Query(...)
):
    try:
        user_id_str = get_clean_user_id(user_id)
        table_name = 'mentor_profiles' if role == 'mentor' else 'mentee_profiles'

        response = supabase.table(table_name) \
                            .select("user_id, embedding, location") \
                            .execute()
        
        profile = find_profile_in_list(response.data, user_id_str)
        
        if profile is None:
            raise HTTPException(status_code=404, detail="User not found (Python search failed)")

        embedding_list = None
        embedding_dim = 0
        embedding_error = None

        # ⭐️ 5. 디버그 API에서도 json.loads()로 실제 차원 계산 ⭐️
        try:
            if profile.get('embedding'):
                embedding_list = json.loads(profile['embedding'])
                embedding_dim = len(embedding_list) # 이제 '384'가 찍힐 것
        except Exception as e:
            embedding_error = f"Failed to parse embedding string: {e}"

        result = {
            "user_id": profile['user_id'],
            "has_embedding": embedding_list is not None,
            "embedding_dimension": embedding_dim, # ⭐️ 4718 대신 384
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