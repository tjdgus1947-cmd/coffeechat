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
import unicodedata
import json
import logging
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

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
    all_data = []
    offset = 0
    while True:
        try:
            response = supabase.table(table_name) \
                             .select(select_query) \
                             .range(offset, offset + chunk_size - 1) \
                             .execute()
            if response.data:
                all_data.extend(response.data)
                if len(response.data) < chunk_size: break
                offset += chunk_size
            else:
                break
        except Exception as e:
            logger.error(f"Error fetching {table_name}: {e}")
            raise e 
    return all_data

# ... (중간 임베딩/위치 업데이트 API 생략 - 기존 유지) ...

@router.get("/api/matching/find-matches-advanced")
def find_matches_advanced(
    user_id: str = Query(...),
    role: str = Query(...),
    limit: int = Query(10, ge=1, le=100),
    max_distance: float = Query(50.0, ge=1),
    keyword_boost: float = Query(0.15, ge=0, le=0.3),
    use_reranking: bool = Query(True),
    use_hybrid: bool = Query(True),
    use_personalization: bool = Query(True)
):
    try:
        user_id_str = get_clean_user_id(user_id)
        current_table = 'mentee_profiles' if role == 'mentee' else 'mentor_profiles'
        target_table = 'mentor_profiles' if role == 'mentee' else 'mentee_profiles'

        if role == 'mentee':
            current_text_column = "current_situation"
            target_text_column = "career_info"
        else:
            current_text_column = "career_info"
            target_text_column = "current_situation"

        # 1. 내 정보
        all_current_profiles = fetch_all_with_pagination(
            current_table, 
            f"*" 
        )
        current_profile = find_profile_in_list(all_current_profiles, user_id_str)
        
        if not current_profile:
            logger.error(f"❌ 내 프로필을 찾을 수 없음. ID: {user_id_str}")
            raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
        
        try:
            current_embedding = json.loads(current_profile['embedding'])
            current_lat, current_lon = extract_coordinates_from_geography(current_profile['location'])
            current_text = current_profile.get(current_text_column, "")
        except Exception as e:
            logger.error(f"❌ 내 프로필 데이터 파싱 실패: {e}")
            raise HTTPException(status_code=500, detail="내 프로필 데이터가 올바르지 않습니다.")
        
        # ⭐️ 2. [핵심 수정] 후보군 가져올 때 '이름(full_name)'과 'ID' 포함하기
        # users 테이블을 조인해서 full_name을 가져옵니다.
        logger.info("📍 1단계: 기본 매칭 시작")
        
        all_candidates_data = fetch_all_with_pagination(
            target_table,
            f"user_id, id, embedding, location, {target_text_column}, users(full_name)"
        )
        
        matches = []
        skip_count = 0

        for candidate in all_candidates_data:
            # 나 자신 제외
            if get_clean_user_id(candidate.get('user_id', '')) == user_id_str:
                continue
            
            try:
                if not candidate.get('embedding') or not candidate.get('location'):
                    skip_count += 1
                    continue

                cand_emb = json.loads(candidate['embedding'])
                cand_lat, cand_lon = extract_coordinates_from_geography(candidate['location'])
                cand_text = candidate.get(target_text_column, "")
                
                # ⭐️ 이름 추출 로직
                user_info = candidate.get('users') or {}
                # users가 리스트로 올 경우 처리 (Supabase 설정에 따라 다름)
                if isinstance(user_info, list) and len(user_info) > 0:
                    cand_name = user_info[0].get('full_name', '알 수 없음')
                elif isinstance(user_info, dict):
                    cand_name = user_info.get('full_name', '알 수 없음')
                else:
                    cand_name = '알 수 없음'
                
                # 점수 계산
                match_result = calculate_final_match_score(
                    current_embedding, cand_emb,
                    current_lat, current_lon,
                    cand_lat, cand_lon,
                    text1=current_text, text2=cand_text,
                    max_distance=max_distance, keyword_boost=keyword_boost
                )
                
                matches.append({
                    "user_id": candidate['user_id'],
                    "id": candidate['id'],
                    "name": cand_name,
                    "text": cand_text,
                    # "embedding": cand_emb, # 굳이 안 보내도 됨
                    "final_score": match_result['final_score'],
                    "text_similarity": match_result['text_similarity'],
                    "distance_km": match_result['distance_km'],
                    "distance_score": match_result['distance_score'],
                    "breakdown": match_result['breakdown']
                })
            except Exception as e:
                # 🔥 [핵심] 에러가 나면 로그를 찍습니다!
                logger.error(f"⚠️ 후보자({candidate.get('id')}) 계산 중 에러: {e}")
                skip_count += 1
                continue
        
        logger.info(f"✅ 매칭 완료: 총 {len(matches)}명 발견 (스킵됨: {skip_count}명)")
        
        matches.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 3. 하이브리드 / 리랭킹 / 개인화 (기존 로직 유지)
        if use_hybrid and len(matches) > 0:
             try:
                semantic_w, keyword_w = adaptive_hybrid_weights(len(current_text))
                matches = hybrid_search(current_text, current_embedding, matches, semantic_w, keyword_w)
             except Exception as e:
                logger.error(f"⚠️ 하이브리드 서치 실패: {e}")

        if use_reranking and len(matches) > limit:
             try:
                matches = rerank_candidates(current_text, matches, top_k=limit * 2)
             except Exception as e:
                logger.error(f"⚠️ 리랭킹 실패: {e}")

        if use_personalization and role == 'mentee':
             try:
                matches = personalize_match_scores(user_id_str, matches, role)
             except Exception as e:
                logger.error(f"⚠️ 개인화 실패: {e}")

        final_matches = matches[:limit]
        
        # 정리 (무거운 embedding 제거)
        for match in final_matches:
            match.pop('embedding', None)
        
        return { "matches": final_matches }

    except Exception as e:
        logger.error(f"❌ 매칭 시스템 치명적 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 레거시 지원 (유지)
@router.get("/api/matching/find-matches")
def find_matches_legacy(
    user_id: str = Query(...),
    role: str = Query(...),
    limit: int = Query(10, ge=1, le=100)
):
    return find_matches_advanced(
        user_id=user_id, 
        role=role, 
        limit=limit,
        max_distance=50.0,       # Query(...) 객체 대신 숫자 50.0 전달
        keyword_boost=0.15,      # 숫자 전달
        use_reranking=True,      # 불리언 전달
        use_hybrid=True,
        use_personalization=True
    )