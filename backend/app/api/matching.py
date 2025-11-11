# backend/app/api/matching.py
# (기존 코드 + 위치 기반 매칭 추가)
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from app.core.config import supabase
from app.services.ml_service import generate_embedding
from app.services.matching_service import (
    calculate_final_match_score,
    extract_coordinates_from_geography
)
import uuid

router = APIRouter()

class EmbeddingRequest(BaseModel):
    user_id: uuid.UUID
    role: str
    text_data: str

class LocationMatchRequest(BaseModel):
    user_id: uuid.UUID
    role: str
    latitude: float
    longitude: float

# ========== 기존 API (임베딩 생성) ==========
@router.post("/api/matching/generate-embedding")
def create_embedding_and_update(request: EmbeddingRequest):
    """
    텍스트 데이터를 AI 임베딩으로 변환하고 DB 업데이트
    """
    try:
        embedding = generate_embedding(request.text_data)
        
        table_name = ""
        if request.role == 'mentor':
            table_name = 'mentor_profiles'
        elif request.role == 'mentee':
            table_name = 'mentee_profiles'
        else:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        response = supabase.table(table_name) \
                           .update({"embedding": embedding}) \
                           .eq("user_id", str(request.user_id)) \
                           .execute()
        
        if response.count == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {"message": f"{request.role} {request.user_id}의 임베딩이 생성되었습니다."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 신규 API (위치 업데이트) ==========
@router.post("/api/matching/update-location")
def update_user_location(request: LocationMatchRequest):
    """
    사용자의 위치 정보를 실시간 업데이트 (PostGIS Point 형식)
    
    Args:
        user_id: 사용자 ID
        role: 'mentor' 또는 'mentee'
        latitude: 위도 (예: 37.4979)
        longitude: 경도 (예: 127.0276)
    """
    try:
        table_name = 'mentor_profiles' if request.role == 'mentor' else 'mentee_profiles'
        
        # PostGIS Point 형식으로 변환 (경도, 위도 순서 주의!)
        geography_point = f"POINT({request.longitude} {request.latitude})"
        
        response = supabase.table(table_name) \
                           .update({"location": geography_point}) \
                           .eq("user_id", str(request.user_id)) \
                           .execute()
        
        if response.count == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {
            "message": "위치 정보가 업데이트되었습니다.",
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 신규 API (통합 매칭 검색) ==========
@router.get("/api/matching/find-matches")
def find_matches_with_location(
    user_id: str = Query(..., description="현재 사용자 ID"),
    role: str = Query(..., description="'mentor' 또는 'mentee'"),
    limit: int = Query(10, ge=1, le=50, description="반환할 최대 매칭 수"),
    max_distance: float = Query(50.0, ge=1, description="최대 거리 기준 (km)")
):
    """
    자기소개(70%) + 거리(30%)를 고려한 최적 매칭 후보 검색
    
    Returns:
        - matches: 매칭 점수 순으로 정렬된 후보 목록
        - 각 매칭 정보:
            * user_id: 후보 사용자 ID
            * final_score: 최종 매칭 점수 (0~100)
            * text_similarity: 텍스트 유사도 (0~100)
            * distance_km: 실제 거리 (km)
            * distance_score: 거리 점수 (0~100)
    """
    try:
        # 1. 현재 사용자 정보 가져오기
        current_table = 'mentee_profiles' if role == 'mentee' else 'mentor_profiles'
        target_table = 'mentor_profiles' if role == 'mentee' else 'mentee_profiles'
        
        current_response = supabase.table(current_table) \
                                   .select("embedding, location") \
                                   .eq("user_id", user_id) \
                                   .execute()
        
        if not current_response.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        current_profile = current_response.data[0]
        
        # 임베딩 확인
        if not current_profile.get('embedding'):
            raise HTTPException(
                status_code=400,
                detail="임베딩이 생성되지 않았습니다. 먼저 /generate-embedding을 호출하세요."
            )
        
        # 위치 확인
        if not current_profile.get('location'):
            raise HTTPException(
                status_code=400,
                detail="위치 정보가 없습니다. 먼저 /update-location을 호출하세요."
            )
        
        current_embedding = current_profile['embedding']
        current_lat, current_lon = extract_coordinates_from_geography(
            current_profile['location']
        )
        
        # 2. 모든 매칭 후보 가져오기 (임베딩과 위치가 모두 있는 경우만)
        candidates_response = supabase.table(target_table) \
                                      .select("user_id, embedding, location") \
                                      .not_.is_("embedding", "null") \
                                      .not_.is_("location", "null") \
                                      .execute()
        
        # 3. 각 후보와의 매칭 점수 계산
        matches = []
        for candidate in candidates_response.data:
            # 자기 자신 제외
            if candidate['user_id'] == user_id:
                continue
            
            try:
                candidate_lat, candidate_lon = extract_coordinates_from_geography(
                    candidate['location']
                )
                
                # 통합 매칭 점수 계산
                match_result = calculate_final_match_score(
                    text_embedding1=current_embedding,
                    text_embedding2=candidate['embedding'],
                    lat1=current_lat,
                    lon1=current_lon,
                    lat2=candidate_lat,
                    lon2=candidate_lon,
                    text_weight=0.7,
                    distance_weight=0.3,
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
                # 특정 후보 처리 실패 시 로그만 남기고 계속 진행
                print(f"Failed to process candidate {candidate['user_id']}: {e}")
                continue
        
        # 4. 최종 점수 높은 순으로 정렬
        matches.sort(key=lambda x: x['final_score'], reverse=True)
        
        return {
            "user_id": user_id,
            "role": role,
            "total_matches": len(matches),
            "matches": matches[:limit]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 디버깅용 API ==========
@router.get("/api/matching/debug/{user_id}")
def debug_user_profile(user_id: str, role: str = Query(...)):
    """
    사용자의 임베딩과 위치 정보 확인 (디버깅용)
    """
    try:
        table_name = 'mentor_profiles' if role == 'mentor' else 'mentee_profiles'
        
        response = supabase.table(table_name) \
                           .select("user_id, embedding, location") \
                           .eq("user_id", user_id) \
                           .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = response.data[0]
        
        result = {
            "user_id": profile['user_id'],
            "has_embedding": profile.get('embedding') is not None,
            "embedding_dimension": len(profile['embedding']) if profile.get('embedding') else 0,
            "has_location": profile.get('location') is not None,
            "location_raw": profile.get('location')
        }
        
        # 위치 정보가 있으면 파싱
        if profile.get('location'):
            try:
                lat, lon = extract_coordinates_from_geography(profile['location'])
                result['location_parsed'] = {
                    "latitude": lat,
                    "longitude": lon
                }
            except Exception as e:
                result['location_error'] = str(e)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))