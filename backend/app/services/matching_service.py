# backend/app/services/matching_service.py
"""
자기소개(70%) + 거리(30%)를 결합한 AI 매칭 시스템
"""
from typing import List, Dict, Tuple
import math
from app.services.ml_service import calculate_match_score
# ml_service.py에 calculate_match_score 함수가 추가되었습니다

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 좌표 간의 거리 계산 (Haversine 공식, km 단위)
    
    Args:
        lat1, lon1: 첫 번째 지점의 위도, 경도
        lat2, lon2: 두 번째 지점의 위도, 경도
    
    Returns:
        float: 두 지점 간의 직선 거리 (km)
    """
    R = 6371  # 지구 반지름 (km)
    
    # 라디안 변환
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine 공식
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def distance_to_score(distance_km: float, max_distance: float = 50.0) -> float:
    """
    거리를 0~100 점수로 변환
    
    Args:
        distance_km: 실제 거리 (km)
        max_distance: 최대 거리 기준 (기본값: 50km)
    
    Returns:
        float: 0~100 사이의 거리 점수
        - 0km = 100점 (가장 가까움)
        - max_distance 이상 = 0점 (너무 멀음)
    
    Examples:
        distance_to_score(0) -> 100.0
        distance_to_score(25) -> 50.0  (50km 기준 시)
        distance_to_score(50) -> 0.0
        distance_to_score(100) -> 0.0
    """
    if distance_km <= 0:
        return 100.0
    if distance_km >= max_distance:
        return 0.0
    
    # 선형적으로 감소
    score = 100 * (1 - distance_km / max_distance)
    return round(score, 2)


def calculate_final_match_score(
    text_embedding1: List[float],
    text_embedding2: List[float],
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    text_weight: float = 0.7,      # 자기소개 가중치 70%
    distance_weight: float = 0.3,  # 거리 가중치 30%
    max_distance: float = 50.0     # 최대 거리 기준 (km)
) -> Dict[str, float]:
    """
    최종 매칭 점수 계산 (자기소개 70% + 거리 30%)
    
    Args:
        text_embedding1, text_embedding2: 각 사용자의 텍스트 임베딩
        lat1, lon1: 첫 번째 사용자의 위도, 경도
        lat2, lon2: 두 번째 사용자의 위도, 경도
        text_weight: 텍스트 유사도 가중치 (기본값: 0.7)
        distance_weight: 거리 점수 가중치 (기본값: 0.3)
        max_distance: 거리 점수 계산 시 최대 거리 (기본값: 50km)
    
    Returns:
        Dict containing:
        - text_similarity: 자기소개 유사도 점수 (0~100)
        - distance_km: 실제 거리 (km)
        - distance_score: 거리 점수 (0~100)
        - final_score: 최종 매칭 점수 (0~100)
        - breakdown: 점수 구성 상세 정보
    """
    # 1. 텍스트 유사도 계산 (0~100)
    text_similarity = calculate_match_score(text_embedding1, text_embedding2)
    
    # 2. 거리 계산
    distance_km = calculate_distance_km(lat1, lon1, lat2, lon2)
    
    # 3. 거리를 점수로 변환 (0~100)
    distance_score = distance_to_score(distance_km, max_distance)
    
    # 4. 최종 점수 계산 (가중 평균)
    final_score = (text_similarity * text_weight) + (distance_score * distance_weight)
    
    return {
        "text_similarity": round(text_similarity, 2),
        "distance_km": distance_km,
        "distance_score": round(distance_score, 2),
        "final_score": round(final_score, 2),
        "breakdown": {
            "text_contribution": round(text_similarity * text_weight, 2),
            "distance_contribution": round(distance_score * distance_weight, 2)
        }
    }


def extract_coordinates_from_geography(geography_point: str) -> Tuple[float, float]:
    """
    PostGIS Geography 포인트에서 위도/경도 추출
    
    Args:
        geography_point: PostGIS Point 형식 (예: "POINT(127.0276 37.4979)")
    
    Returns:
        Tuple[float, float]: (latitude, longitude)
    
    Raises:
        ValueError: 잘못된 형식의 geography 데이터인 경우
    """
    try:
        # "POINT(경도 위도)" 형식 파싱
        coords = geography_point.replace("POINT(", "").replace(")", "").split()
        longitude = float(coords[0])
        latitude = float(coords[1])
        return latitude, longitude
    except Exception as e:
        raise ValueError(f"Invalid geography format: {geography_point}") from e