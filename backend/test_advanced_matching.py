# backend/test_advanced_matching.py
from app.services.hybrid_search_service import BM25

# 간단한 테스트
corpus = [
    "Python 백엔드 개발자 3년차",
    "React 프론트엔드 개발자 5년차", 
    "Python Django 풀스택 개발자"
]

bm25 = BM25(corpus)
query = "Python 백엔드"

scores = bm25.get_scores(query)
print("BM25 점수:", scores)
# 출력: [높은 점수, 낮은 점수, 중간 점수]