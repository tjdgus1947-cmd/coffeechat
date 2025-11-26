# backend/test_improved_matching.py
from app.services.ml_service import generate_embedding, calculate_match_score

# 테스트 케이스
text1 = "Python 백엔드 개발자 3년차, FastAPI와 Django 경험 있습니다"
text2 = "5년차 백엔드 개발자입니다. Python, FastAPI로 API 서버 개발 경험이 많습니다"

# 임베딩 생성
emb1 = generate_embedding(text1)
emb2 = generate_embedding(text2)

# 유사도 계산 (키워드 보너스 포함)
score_with_keyword = calculate_match_score(emb1, emb2, text1, text2, keyword_weight=0.15)
score_without_keyword = calculate_match_score(emb1, emb2)

print(f"키워드 보너스 없음: {score_without_keyword}점")
print(f"키워드 보너스 포함: {score_with_keyword}점")
print(f"차이: +{score_with_keyword - score_without_keyword}점")