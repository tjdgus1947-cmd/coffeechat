# backend/app/services/ml_service.py

from sentence_transformers import SentenceTransformer
import math

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


def calculate_distance_score(mentee_lat: float, mentee_lon: float, mentor_lat: float, mentor_lon: float) -> tuple:
    """
    멘티와 멘토 사이의 거리를 계산하고 거리 점수를 반환합니다.
    
    Returns:
        tuple: (거리_km, 거리_점수_0to100)
    """
    if None in [mentee_lat, mentee_lon, mentor_lat, mentor_lon]:
        return (None, 0.0)
    
    # Haversine 공식으로 거리 계산 (km)
    R = 6371  # 지구 반지름 (km)
    
    lat1_rad = math.radians(mentee_lat)
    lat2_rad = math.radians(mentor_lat)
    delta_lat = math.radians(mentor_lat - mentee_lat)
    delta_lon = math.radians(mentor_lon - mentee_lon)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance_km = R * c
    
    # 거리 점수 계산 (가까울수록 높은 점수)
    # 0km = 100점, 10km = 50점, 50km 이상 = 0점
    if distance_km <= 10:
        distance_score = 100 - (distance_km * 5)  # 0~10km: 100~50점
    elif distance_km <= 50:
        distance_score = 50 - ((distance_km - 10) * 1.25)  # 10~50km: 50~0점
    else:
        distance_score = 0.0
    
    return (round(distance_km, 2), round(max(0, distance_score), 1))


def calculate_final_score(text_similarity: float, distance_score: float) -> float:
    """
    텍스트 유사도와 거리 점수를 가중 평균하여 최종 매칭 점수를 계산합니다.
    
    Args:
        text_similarity: 0~1 사이의 텍스트 유사도 (코사인 유사도)
        distance_score: 0~100 사이의 거리 점수
    
    Returns:
        float: 0~100 사이의 최종 매칭 점수
    """
    # 텍스트 유사도를 0~100 스케일로 변환
    text_score = text_similarity * 100
    
    # 가중 평균: 텍스트 70% + 거리 30%
    final_score = (text_score * 0.7) + (distance_score * 0.3)
    
    return round(final_score, 1)