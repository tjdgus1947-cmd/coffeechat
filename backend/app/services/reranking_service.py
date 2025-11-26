# backend/app/services/reranking_service.py
"""
2단계 Re-ranking 시스템
1단계: bge-m3로 빠르게 후보 100명 추출
2단계: Cross-Encoder로 정밀 재평가
"""
from sentence_transformers import CrossEncoder
from typing import List, Dict
import torch

# GPU 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# 🔥 Cross-Encoder 모델 로드 (한국어 특화)
try:
    # 옵션 1: 다국어 모델 (추천)
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512, device=device)
    print(f"✅ Re-ranker 모델 로드 성공 (device: {device})")
except Exception as e:
    print(f"⚠️ Re-ranker 로드 실패: {e}")
    reranker = None


def rerank_candidates(
    query_text: str,
    candidates: List[Dict],
    top_k: int = 10,
    rerank_weight: float = 0.3  # Re-rank 점수 가중치
) -> List[Dict]:
    """
    후보들을 Cross-Encoder로 재평가하여 재순위화
    
    Args:
        query_text: 현재 사용자의 자기소개 텍스트
        candidates: 1차 매칭 결과 (user_id, final_score, text 포함)
        top_k: 최종 반환할 개수
        rerank_weight: Re-rank 점수 반영 비율 (0~1)
    
    Returns:
        재순위화된 후보 목록
    """
    if not reranker or not candidates:
        return candidates[:top_k]
    
    if len(candidates) <= top_k:
        return candidates  # 재순위화 불필요
    
    print(f"🔄 Re-ranking {len(candidates)}명 → {top_k}명...")
    
    try:
        # 1. Cross-Encoder 점수 계산
        candidate_texts = [c.get('text', '') for c in candidates]
        pairs = [[query_text, text] for text in candidate_texts]
        
        # 배치 처리로 점수 계산
        cross_scores = reranker.predict(pairs, show_progress_bar=False)
        
        # 2. 기존 점수와 결합
        for i, candidate in enumerate(candidates):
            original_score = candidate.get('final_score', 0)
            cross_score = float(cross_scores[i]) * 100  # 0~100 스케일로 변환
            
            # 가중 평균
            combined_score = (
                original_score * (1 - rerank_weight) +
                cross_score * rerank_weight
            )
            
            candidate['rerank_score'] = round(cross_score, 2)
            candidate['combined_score'] = round(combined_score, 2)
        
        # 3. 재정렬
        candidates.sort(key=lambda x: x['combined_score'], reverse=True)
        
        print(f"✅ Re-ranking 완료")
        return candidates[:top_k]
    
    except Exception as e:
        print(f"⚠️ Re-ranking 실패, 원본 순서 반환: {e}")
        return candidates[:top_k]


def rerank_with_diversity(
    query_text: str,
    candidates: List[Dict],
    top_k: int = 10,
    diversity_penalty: float = 0.1
) -> List[Dict]:
    """
    다양성을 고려한 Re-ranking
    - 비슷한 후보들이 연속으로 나오지 않도록 조정
    """
    if not reranker or len(candidates) <= top_k:
        return candidates[:top_k]
    
    # 1. 기본 Re-ranking
    reranked = rerank_candidates(query_text, candidates, top_k * 2, rerank_weight=0.3)
    
    # 2. 다양성 선택 (Maximal Marginal Relevance)
    selected = []
    remaining = reranked.copy()
    
    # 첫 번째는 무조건 최고 점수
    selected.append(remaining.pop(0))
    
    while len(selected) < top_k and remaining:
        best_idx = 0
        best_score = -1
        
        for i, candidate in enumerate(remaining):
            # 기본 점수
            relevance = candidate.get('combined_score', 0)
            
            # 이미 선택된 후보들과의 유사도 계산 (간단히 거리로)
            max_similarity = 0
            for sel in selected:
                # 거리 기반 유사도 (가까울수록 유사)
                dist_diff = abs(candidate.get('distance_km', 100) - sel.get('distance_km', 100))
                similarity = max(0, 1 - dist_diff / 50)  # 50km 기준
                max_similarity = max(max_similarity, similarity)
            
            # 다양성 페널티 적용
            diversity_score = relevance - (diversity_penalty * 100 * max_similarity)
            
            if diversity_score > best_score:
                best_score = diversity_score
                best_idx = i
        
        selected.append(remaining.pop(best_idx))
    
    return selected