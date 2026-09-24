# backend/app/services/hybrid_search_service.py
"""
하이브리드 검색: Semantic + Keyword (BM25)
- 의미적 유사도: bge-m3 임베딩
- 키워드 매칭: BM25 알고리즘
"""
from typing import Dict, List
import math
from collections import Counter
import re


HANGUL_RE = re.compile(r'[가-힣]')


def tokenize(text: str) -> List[str]:
    """
    BM25 용 토큰화.
    - 영문/숫자: 공백 단위 단어
    - 한글: 공백 단위로 자르면 조사가 붙어 "데이터를" ≠ "데이터" 가 되므로,
      단어를 글자 2개씩 겹쳐 자른 bigram 으로 만든다 ("데이터를" → 데이, 이터, 터를).
      형태소 분석기 없이 조사·어미 차이를 흡수하는 방법 (Elasticsearch CJK bigram 과 같은 방식)
    """
    text = re.sub(r'[^\w\s가-힣]', ' ', (text or '').lower())
    tokens: List[str] = []
    for word in text.split():
        if HANGUL_RE.search(word) and len(word) >= 2:
            tokens.extend(word[i:i + 2] for i in range(len(word) - 1))
        else:
            tokens.append(word)
    return tokens


class BM25:
    """
    BM25 알고리즘 구현 (키워드 기반 검색)
    score(q, d) = Σ IDF(t) · f(t,d)·(k1+1) / (f(t,d) + k1·(1 - b + b·|d|/avgdl))
    """
    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs = [Counter(tokenize(doc)) for doc in corpus]
        self.doc_lens = [sum(freqs.values()) for freqs in self.doc_freqs]
        self.corpus_size = len(corpus)
        # 문서 길이는 IDF/점수 계산과 같은 토큰 기준으로 센다
        self.avgdl = (sum(self.doc_lens) / self.corpus_size) if self.corpus_size else 0.0

        df: Dict[str, int] = {}
        for freqs in self.doc_freqs:
            for word in freqs:
                df[word] = df.get(word, 0) + 1
        self.idf = {
            word: math.log((self.corpus_size - n + 0.5) / (n + 0.5) + 1)
            for word, n in df.items()
        }

    def score(self, query: str, doc_idx: int) -> float:
        """쿼리와 문서 간의 BM25 점수 계산"""
        freqs = self.doc_freqs[doc_idx]
        doc_len = self.doc_lens[doc_idx]
        if not self.avgdl:
            return 0.0
        total = 0.0
        for word in set(tokenize(query)):
            f = freqs.get(word)
            if not f:
                continue
            total += self.idf[word] * (f * (self.k1 + 1)) / (
                f + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            )
        return total

    def get_scores(self, query: str) -> List[float]:
        """모든 문서에 대한 BM25 점수 반환"""
        return [self.score(query, i) for i in range(self.corpus_size)]


def hybrid_search(
    query_text: str,
    query_embedding: List[float],
    candidates: List[Dict],
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[Dict]:
    """
    하이브리드 검색: Semantic + BM25
    
    Args:
        query_text: 검색 쿼리 텍스트
        query_embedding: 쿼리 임베딩
        candidates: 후보 목록 (text, embedding 포함)
        semantic_weight: 의미 검색 가중치
        keyword_weight: 키워드 검색 가중치
    """
    if not candidates:
        return []
    
    # 1. BM25 점수 계산
    corpus = [c.get('text', '') for c in candidates]
    bm25 = BM25(corpus)
    bm25_scores = bm25.get_scores(query_text)
    
    # BM25 점수 정규화 (0~100)
    max_bm25 = max(bm25_scores) or 1
    bm25_normalized = [(score / max_bm25) * 100 for score in bm25_scores]
    
    # 2. 의미 검색 점수 (이미 계산됨)
    semantic_scores = [c.get('text_similarity', 0) for c in candidates]
    
    # 3. 하이브리드 점수 계산
    for i, candidate in enumerate(candidates):
        semantic = semantic_scores[i]
        keyword = bm25_normalized[i]
        
        # 가중 평균
        hybrid_score = (semantic * semantic_weight) + (keyword * keyword_weight)
        
        candidate['keyword_score'] = round(keyword, 2)
        candidate['hybrid_score'] = round(hybrid_score, 2)
        
        # 텍스트 부분(70%)을 하이브리드 점수로 교체하고, 거리 점수 기여분(30%)은 유지
        distance_contribution = candidate.get('breakdown', {}).get('distance_contribution', 0)
        
        candidate['final_score'] = round(hybrid_score * 0.7 + distance_contribution, 2)
    
    # 재정렬
    candidates.sort(key=lambda x: x['final_score'], reverse=True)
    
    return candidates


def adaptive_hybrid_weights(query_length: int) -> tuple:
    """
    쿼리 길이에 따라 가중치 자동 조정
    - 짧은 쿼리: 키워드 검색 비중 증가
    - 긴 쿼리: 의미 검색 비중 증가
    """
    if query_length < 20:
        # 짧은 쿼리 (키워드 중요)
        return (0.5, 0.5)
    elif query_length < 100:
        # 중간 길이
        return (0.7, 0.3)
    else:
        # 긴 쿼리 (의미 중요)
        return (0.8, 0.2)