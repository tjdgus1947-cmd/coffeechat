# backend/app/services/ml_service.py
from sentence_transformers import SentenceTransformer
import math

# 1. 모델 로드
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("SentenceTransformer 모델 로드 성공")
except Exception as e:
    print(f"SentenceTransformer 모델 로드 실패: {e}")
    model = None

def generate_embedding(text: str):
    """
    주어진 텍스트를 384차원 임베딩 벡터로 변환합니다. (WBS 4.1)
    """
    if model is None:
        raise Exception("ML 모델이 로드되지 않았습니다.")
    if not text:
        return [0.0] * 384
    
    embedding = model.encode(text)
    return embedding.tolist()


def calculate_match_score(embedding1, embedding2):
    """
    두 임베딩 벡터 간의 코사인 유사도를 계산하여 0~100 점수로 반환
    (scikit-learn 없이 순수 Python으로 구현)
    
    Args:
        embedding1: 첫 번째 임베딩 벡터 (list)
        embedding2: 두 번째 임베딩 벡터 (list)
    
    Returns:
        float: 0~100 사이의 유사도 점수
    """
    # 벡터 내적 (dot product)
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    
    # 각 벡터의 크기 (magnitude)
    magnitude1 = math.sqrt(sum(a * a for a in embedding1))
    magnitude2 = math.sqrt(sum(b * b for b in embedding2))
    
    # 코사인 유사도 (-1 ~ 1)
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    cosine_similarity = dot_product / (magnitude1 * magnitude2)
    
    # 0~100 스케일로 변환
    # cosine_similarity: -1(완전 반대) ~ 0(무관) ~ 1(완전 일치)
    # 변환: (-1+1)/2*100 = 0점, (0+1)/2*100 = 50점, (1+1)/2*100 = 100점
    score = (cosine_similarity + 1) / 2 * 100
    
    return round(score, 2)