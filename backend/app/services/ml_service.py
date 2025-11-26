# backend/app/services/ml_service.py
from sentence_transformers import SentenceTransformer, util
import torch

# ⭐️ 1. GPU 가속 설정 (가능하면 GPU 사용)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading AI Model on {device}...")

# ⭐️ 2. 모델 교체 (BAAI/bge-m3: 한국어 성능 우수, 변별력 높음)
try:
    model = SentenceTransformer('BAAI/bge-m3', device=device)
    print("SentenceTransformer (BAAI/bge-m3) 모델 로드 성공")
except Exception as e:
    print(f"SentenceTransformer 모델 로드 실패: {e}")
    model = None

def generate_embedding(text: str) -> list[float]:
    """
    주어진 텍스트를 1024차원 임베딩 벡터로 변환합니다. (BAAI/bge-m3 기준)
    """
    if model is None:
        raise Exception("ML 모델이 로드되지 않았습니다.")
    
    if not text:
        # bge-m3는 1024차원이므로 0 벡터도 1024개여야 함
        return [0.0] * 1024
    
    # normalize_embeddings=True: 코사인 유사도 계산 최적화
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def calculate_match_score(embedding1: list[float], embedding2: list[float]) -> float:
    """
    두 임베딩 벡터 간의 코사인 유사도를 계산하여 0~100 점수로 반환
    """
    if not embedding1 or not embedding2:
        return 0.0

    # ⭐️ 3. 유틸리티 함수 사용 (수동 계산보다 빠르고 정확함)
    # 텐서로 변환하여 계산 후 다시 float로 추출
    score = util.cos_sim(embedding1, embedding2).item()
    
    # 점수 보정 (0~100)
    # 코사인 유사도(-1~1)를 0~100점으로 변환하되, 음수는 0으로 처리
    if score < 0:
        score = 0.0
        
    return round(score * 100, 2)