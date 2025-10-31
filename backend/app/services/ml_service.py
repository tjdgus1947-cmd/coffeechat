# backend/app/services/ml_service.py

from sentence_transformers import SentenceTransformer

# 1. (wbs.md 4.1) 'all-MiniLM-L6-v2' 모델을 로드합니다. (384 차원)
#    이 모델은 처음 실행될 때 자동으로 다운로드됩니다.
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
        # 텍스트가 비어있으면 0으로 채워진 벡터 반환
        return [0.0] * 384

    # 2. 텍스트를 AI 벡터로 변환
    embedding = model.encode(text)

    # 3. 리스트(list) 형태로 변환하여 반환 (DB에 저장하기 위함)
    return embedding.tolist()