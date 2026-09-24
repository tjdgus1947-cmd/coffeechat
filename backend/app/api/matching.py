# backend/app/api/matching.py
"""
AI 매칭 API

파이프라인
  0. 내 프로필 조회 (user_id 로 1건)
  1. 후보 검색: DB 함수 match_candidates 가 pgvector(HNSW)로 임베딩이 가까운 상위 N명만 반환
  2. 1차 점수: 텍스트 유사도 70% + 거리 30% + 키워드 보너스
  3. 하이브리드: 의미 점수 + BM25 키워드 점수
  4. 리랭킹: Cross-Encoder 로 상위 후보 재평가
  5. 개인화: 과거 예약 이력 기반 보너스
각 단계는 final_score 하나만 갱신하고, 다음 단계는 그 값을 이어받는다.
"""
import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import supabase
from app.services.feedback_service import personalize_match_scores
from app.services.hybrid_search_service import adaptive_hybrid_weights, hybrid_search
from app.services.matching_service import (
    calculate_final_match_score,
    extract_coordinates_from_geography,
)
from app.services.reranking_service import rerank_candidates
from .auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

# 1단계에서 DB가 돌려줄 후보 수. 이후 단계(거리 반영, 리랭킹)의 입력 풀이다.
CANDIDATE_POOL_SIZE = 200
# 하이브리드/리랭킹에 넘기는 상위 후보 수
RERANK_POOL_SIZE = 100

ROLE_CONFIG = {
    # 내 역할: (내 프로필 테이블, 내 텍스트 컬럼, 찾을 상대 역할)
    "mentee": ("mentee_profiles", "current_situation", "mentor"),
    "mentor": ("mentor_profiles", "career_info", "mentee"),
}


def parse_embedding(value) -> Optional[List[float]]:
    """PostgREST 는 vector 컬럼을 '[0.1,0.2,...]' 문자열로 돌려준다."""
    if value is None:
        return None
    if isinstance(value, str):
        return json.loads(value)
    return list(value)


@router.get("/api/matching/find-matches-advanced")
def find_matches_advanced(
    role: str = Query(..., pattern="^(mentor|mentee)$"),
    limit: int = Query(10, ge=1, le=100),
    max_distance: float = Query(50.0, ge=1),
    keyword_boost: float = Query(0.15, ge=0, le=0.3),
    use_reranking: bool = Query(True),
    use_hybrid: bool = Query(True),
    use_personalization: bool = Query(True),
    user_id: Optional[str] = Query(None, description="하위 호환용. 사용하지 않음 (토큰의 사용자 기준)"),
    current_user_id: str = Depends(get_current_user_id),
):
    my_table, my_text_column, target_role = ROLE_CONFIG[role]

    try:
        # 0. 내 프로필: 테이블 전체가 아니라 내 행 1건만 조회
        me = (
            supabase.table(my_table)
            .select(f"user_id, embedding, location, {my_text_column}")
            .eq("user_id", current_user_id)
            .limit(1)
            .execute()
        )
        if not me.data:
            raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")

        my_profile = me.data[0]
        my_embedding = parse_embedding(my_profile.get("embedding"))
        if not my_embedding or not my_profile.get("location"):
            raise HTTPException(status_code=422, detail="자기소개 또는 위치 정보가 없어 매칭할 수 없습니다.")

        my_lat, my_lon = extract_coordinates_from_geography(my_profile["location"])
        my_text = my_profile.get(my_text_column) or ""

        # 1. 후보 검색 (DB 에서 벡터 인덱스로 상위 N명)
        candidates_resp = supabase.rpc(
            "match_candidates",
            {
                "query_embedding": my_profile["embedding"],
                "target_role": target_role,
                "exclude_user_id": current_user_id,
                "match_count": CANDIDATE_POOL_SIZE,
            },
        ).execute()
        candidates = candidates_resp.data or []
        logger.info("후보 %d명 조회", len(candidates))

        # 2. 1차 점수
        matches = []
        skipped = 0
        for cand in candidates:
            try:
                cand_embedding = parse_embedding(cand["embedding"])
                cand_lat, cand_lon = extract_coordinates_from_geography(cand["location"])
                cand_text = cand.get("profile_text") or ""

                score = calculate_final_match_score(
                    my_embedding, cand_embedding,
                    my_lat, my_lon, cand_lat, cand_lon,
                    text1=my_text, text2=cand_text,
                    max_distance=max_distance, keyword_boost=keyword_boost,
                )
                matches.append({
                    "user_id": cand["user_id"],
                    "id": cand["id"],
                    "name": cand.get("full_name") or "알 수 없음",
                    "text": cand_text,
                    "final_score": score["final_score"],
                    "text_similarity": score["text_similarity"],
                    "distance_km": score["distance_km"],
                    "distance_score": score["distance_score"],
                    "breakdown": score["breakdown"],
                })
            except Exception as e:
                skipped += 1
                logger.warning("후보 %s 점수 계산 실패: %s", cand.get("id"), e)

        if skipped:
            logger.info("점수 계산에서 %d명 제외", skipped)

        matches.sort(key=lambda m: m["final_score"], reverse=True)
        matches = matches[:RERANK_POOL_SIZE]

        # 3. 하이브리드 (의미 + BM25)
        if use_hybrid and matches:
            try:
                semantic_w, keyword_w = adaptive_hybrid_weights(len(my_text))
                matches = hybrid_search(my_text, my_embedding, matches, semantic_w, keyword_w)
            except Exception as e:
                logger.error("하이브리드 검색 실패, 이전 순위 유지: %s", e)

        # 4. 리랭킹
        if use_reranking and len(matches) > limit:
            try:
                matches = rerank_candidates(my_text, matches, top_k=limit * 2)
            except Exception as e:
                logger.error("리랭킹 실패, 이전 순위 유지: %s", e)

        # 5. 개인화 (멘티만)
        if use_personalization and role == "mentee":
            try:
                matches = personalize_match_scores(current_user_id, matches, role)
            except Exception as e:
                logger.error("개인화 실패, 이전 순위 유지: %s", e)

        return {"matches": matches[:limit]}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("매칭 처리 중 오류: %s", e)
        raise HTTPException(status_code=500, detail="매칭 처리 중 오류가 발생했습니다.")


# 레거시 경로 (프론트가 사용 중)
@router.get("/api/matching/find-matches")
def find_matches_legacy(
    role: str = Query(..., pattern="^(mentor|mentee)$"),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    current_user_id: str = Depends(get_current_user_id),
):
    return find_matches_advanced(
        role=role,
        limit=limit,
        max_distance=50.0,
        keyword_boost=0.15,
        use_reranking=True,
        use_hybrid=True,
        use_personalization=True,
        user_id=user_id,
        current_user_id=current_user_id,
    )
