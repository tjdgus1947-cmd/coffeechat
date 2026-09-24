# backend/app/services/reranking_service.py
"""
2단계 Re-ranking
  1단계: bge-m3 임베딩 + 거리 + BM25 로 후보를 좁힌다 (bi-encoder: 빠르지만 대략적)
  2단계: Cross-Encoder 가 (내 소개, 후보 소개) 쌍을 함께 읽고 관련도를 다시 매긴다 (느리지만 정밀)

모델
  기본값 BAAI/bge-reranker-v2-m3: 한국어를 포함한 다국어 리랭커. 임베딩 모델(bge-m3)과 같은 계열.
  이전 모델 cross-encoder/ms-marco-MiniLM-L-6-v2 는 영어 MS MARCO 로만 학습돼 한국어 소개글에 부적합했다.
  RERANKER_MODEL 환경변수로 교체 가능
  (예: cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 — 더 가볍지만 학습 언어에 한국어가 없음)
"""
import math
import os
from typing import Dict, List

import torch
from sentence_transformers import CrossEncoder

device = "cuda" if torch.cuda.is_available() else "cpu"
RERANKER_MODEL = os.environ.get(
    "RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"
)

try:
    reranker = CrossEncoder(RERANKER_MODEL, max_length=512, device=device)
    print(f"✅ Re-ranker 로드: {RERANKER_MODEL} (device: {device})")
except Exception as e:
    print(f"⚠️ Re-ranker 로드 실패, 리랭킹 없이 동작: {e}")
    reranker = None


def to_probability(logit: float) -> float:
    """Cross-Encoder 출력(로짓, 범위 제한 없음)을 시그모이드로 0~1 로 변환한다.
    기존 점수(0~100)와 섞기 전에 스케일을 맞추기 위함."""
    # exp 오버플로 방지: 부호에 따라 식을 나눠 계산 (수치적으로 안정적인 시그모이드)
    if logit >= 0:
        return 1.0 / (1.0 + math.exp(-logit))
    z = math.exp(logit)
    return z / (1.0 + z)


def rerank_candidates(
    query_text: str,
    candidates: List[Dict],
    top_k: int = 10,
    rerank_weight: float = 0.3,
) -> List[Dict]:
    """
    후보를 Cross-Encoder 로 재평가해 final_score 를 갱신하고 상위 top_k 를 반환한다.

    final_score = 기존 final_score × (1 - w) + rerank_score × w   (둘 다 0~100)
    """
    if not reranker or not candidates or not query_text:
        return candidates[:top_k]

    pairs = [[query_text, c.get("text", "")] for c in candidates]
    logits = reranker.predict(pairs, show_progress_bar=False)

    for cand, logit in zip(candidates, logits):
        rerank_score = to_probability(float(logit)) * 100
        combined = cand.get("final_score", 0) * (1 - rerank_weight) + rerank_score * rerank_weight
        cand["rerank_score"] = round(rerank_score, 2)
        # 다음 단계(개인화)가 이어받을 수 있도록 final_score 자체를 갱신한다
        cand["final_score"] = round(combined, 2)

    candidates.sort(key=lambda c: c["final_score"], reverse=True)
    return candidates[:top_k]
