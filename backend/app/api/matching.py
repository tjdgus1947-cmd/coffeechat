# backend/app/api/matching.py

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

@router.get("/api/matching/find-matches-advanced")
def find_matches_advanced(
    user_id: str = Query(...),
    role: str = Query(...),
    limit: int = Query(10, ge=1, le=100),
    max_distance: float = Query(50.0, ge=1),
    keyword_boost: float = Query(0.15, ge=0, le=0.3),
    use_reranking: bool = Query(True, description="Re-ranking 사용"),
    use_hybrid: bool = Query(True, description="하이브리드 검색 사용"),
    use_personalization: bool = Query(True, description="개인화 사용")
):
    """
    🚀 고급 AI 매칭 API
    - Re-ranking (2단계 검색)
    - 하이브리드 검색 (Semantic + BM25)
    - 개인화 (피드백 학습)
    """
    try:
        user_id_str = get_clean_user_id(user_id)
        current_table = 'mentee_profiles' if role == 'mentee' else 'mentor_profiles'
        target_table = 'mentor_profiles' if role == 'mentee' else 'mentee_profiles'

        # 텍스트 컬럼 설정
        if role == 'mentee':
            current_text_column = "current_situation"
            target_text_column = "career_info"
        else:
            current_text_column = "career_info"
            target_text_column = "current_situation"

        # 현재 사용자 정보
        all_current_profiles = fetch_all_with_pagination(
            current_table, 
            f"user_id, embedding, location, {current_text_column}"
        )
        current_profile = find_profile_in_list(all_current_profiles, user_id_str)
        
        if not current_profile:
            raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
        
        current_embedding = json.loads(current_profile['embedding'])
        current_lat, current_lon = extract_coordinates_from_geography(current_profile['location'])
        current_text = current_profile.get(current_text_column, "")
        
        # 1️⃣ 1차 매칭 (기본 임베딩 + 거리)
        logger.info("📍 1단계: 기본 매칭 시작")
        
        all_candidates_data = []
        offset = 0
        chunk_size = 1000
        
        while True:
            candidates_response = supabase.table(target_table) \
                .select(f"user_id, embedding, location, {target_text_column}") \
                .not_.is_("embedding", "null") \
                .not_.is_("location", "null") \
                .range(offset, offset + chunk_size - 1) \
                .execute()
            
            if candidates_response.data:
                all_candidates_data.extend(candidates_response.data)
                if len(candidates_response.data) < chunk_size:
                    break
                offset += chunk_size
            else:
                break
        
        logger.info(f"총 후보: {len(all_candidates_data)}명")

        matches = []
        for candidate in all_candidates_data:
            if get_clean_user_id(candidate.get('user_id', '')) == user_id_str:
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
        logger.info(f"1차 매칭 완료: {len(matches)}명")
        
        # 2️⃣ 하이브리드 검색 (선택)
        if use_hybrid and len(matches) > 0:
            logger.info("🔍 2단계: 하이브리드 검색 적용")
            query_len = len(current_text)
            semantic_w, keyword_w = adaptive_hybrid_weights(query_len)
            
            matches = hybrid_search(
                current_text,
                current_embedding,
                matches,
                semantic_weight=semantic_w,
                keyword_weight=keyword_w
            )
        
        # 3️⃣ Re-ranking (선택)
        if use_reranking and len(matches) > limit:
            logger.info("🎯 3단계: Re-ranking 적용")
            matches = rerank_candidates(
                current_text,
                matches,
                top_k=limit * 2,  # 여유있게
                rerank_weight=0.3
            )
        
        # 4️⃣ 개인화 (선택)
        if use_personalization and role == 'mentee':
            logger.info("✨ 4단계: 개인화 적용")
            matches = personalize_match_scores(user_id_str, matches, role)
        
        # 최종 정리
        final_matches = matches[:limit]
        
        # 응답 데이터 정리 (embedding, text 제거)
        for match in final_matches:
            match.pop('embedding', None)
            match.pop('text', None)
        
        return {
            "user_id": user_id,
            "total_candidates": len(all_candidates_data),
            "filtered_matches": len(matches),
            "matches": final_matches,
            "settings": {
                "keyword_boost": keyword_boost,
                "use_reranking": use_reranking,
                "use_hybrid": use_hybrid,
                "use_personalization": use_personalization
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"고급 매칭 실패: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))