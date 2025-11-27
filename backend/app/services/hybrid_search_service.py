# backend/app/services/hybrid_search_service.py
"""
하이브리드 검색: Semantic + Keyword (BM25)
- 의미적 유사도: bge-m3 임베딩
- 키워드 매칭: BM25 알고리즘
"""
from typing import List, Dict
import math
from collections import Counter
import re


class BM25:
    """
    BM25 알고리즘 구현 (키워드 기반 검색)
    """
    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(doc.split()) for doc in corpus) / self.corpus_size
        
        # 문서 빈도 계산
        self.doc_freqs = []
        self.idf = {}
        
        for doc in corpus:
            frequencies = Counter(self._tokenize(doc))
            self.doc_freqs.append(frequencies)
            
            for word in frequencies.keys():
                self.idf[word] = self.idf.get(word, 0) + 1
        
        # IDF 계산
        for word, freq in self.idf.items():
            self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)
    
    def _tokenize(self, text: str) -> List[str]:
        """텍스트 토큰화 (한글/영문 모두 지원)"""
        # 한글, 영문, 숫자만 남기고 소문자 변환
        text = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
        return text.split()
    
    def score(self, query: str, doc_idx: int) -> float:
        """쿼리와 문서 간의 BM25 점수 계산"""
        score = 0
        doc_freqs = self.doc_freqs[doc_idx]
        doc_len = sum(doc_freqs.values())
        
        for word in self._tokenize(query):
            if word not in doc_freqs:
                continue
            
            freq = doc_freqs[word]
            idf = self.idf.get(word, 0)
            
            score += idf * (freq * (self.k1 + 1)) / \
                     (freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl))
        
        return score
    
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
    
    print(f"🔍 하이브리드 검색 시작 ({len(candidates)}명)")
    
    # 1. BM25 점수 계산
    corpus = [c.get('text', '') for c in candidates]
    bm25 = BM25(corpus)
    bm25_scores = bm25.get_scores(query_text)
    
    # BM25 점수 정규화 (0~100)
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
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
        
        # 기존 final_score 업데이트
        original_final = candidate.get('final_score', 0)
        # 거리 점수 비율 유지
        distance_contribution = candidate.get('breakdown', {}).get('distance_contribution', 0)
        
        candidate['final_score'] = round(hybrid_score * 0.7 + distance_contribution, 2)
    
    # 재정렬
    candidates.sort(key=lambda x: x['final_score'], reverse=True)
    
    print(f"✅ 하이브리드 검색 완료")
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