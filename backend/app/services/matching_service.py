# backend/app/services/matching_service.py
"""
자기소개(70%) + 거리(30%) + 키워드 보너스 매칭 시스템
"""
from typing import List, Dict, Tuple
import math
import re
from app.services.ml_service import calculate_match_score

try:
    from shapely import wkb
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("⚠️ 경고: shapely 라이브러리가 없습니다.")


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 좌표 간의 거리 계산 (Haversine 공식, km 단위)
    """
    R = 6371  # 지구 반지름 (km)
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def distance_to_score(distance_km: float, max_distance: float = 50.0) -> float:
    """
    거리를 0~100 점수로 변환 (비선형 스케일)
    """
    if distance_km <= 0:
        return 100.0
    if distance_km >= max_distance:
        return 0.0
    
    # 비선형: 가까울수록 점수 급상승
    normalized = distance_km / max_distance
    score = 100 * (1 - normalized ** 0.7)
    
    return round(score, 2)


def calculate_final_match_score(
    text_embedding1: List[float],
    text_embedding2: List[float],
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    text1: str = "",  # 🔥 원본 텍스트 (키워드 매칭용)
    text2: str = "",
    text_weight: float = 0.7,
    distance_weight: float = 0.3,
    max_distance: float = 50.0,
    keyword_boost: float = 0.15  # 🔥 키워드 가중치
) -> Dict[str, float]:
    """
    최종 매칭 점수 계산
    - 임베딩 유사도 70%
    - 거리 점수 30%
    - 키워드 보너스 적용
    """
    # 1. 텍스트 유사도 계산 (키워드 가중치 포함)
    text_similarity = calculate_match_score(
        text_embedding1, 
        text_embedding2,
        text1=text1,
        text2=text2,
        keyword_weight=keyword_boost  # 🔥 ml_service의 키워드 기능 활용
    )
    
    # 2. 거리 계산
    distance_km = calculate_distance_km(lat1, lon1, lat2, lon2)
    distance_score = distance_to_score(distance_km, max_distance)
    
    # 3. 최종 점수 (가중 평균)
    final_score = (text_similarity * text_weight) + (distance_score * distance_weight)
    
    # 4. 보너스: 둘 다 우수한 경우 추가 점수
    if text_similarity > 80 and distance_score > 70:
        boost = min((text_similarity - 80) * 0.1, 5)
        final_score = min(final_score + boost, 100)
    
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


def extract_coordinates_from_geography(geography_data: str) -> Tuple[float, float]:
    """
    PostGIS Geography (WKB 또는 WKT)에서 위도/경도 추출
    """
    if not geography_data:
        raise ValueError("Location data is empty or None")

    try:
        # 1순위: WKB(16진수) 처리
        if SHAPELY_AVAILABLE and re.match(r"^[0-9A-Fa-f]+$", geography_data):
            point = wkb.loads(geography_data, hex=True)
            return (point.y, point.x)

        # 2순위: WKT(텍스트) 처리
        match = re.search(
            r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", geography_data, re.IGNORECASE
        )
        if match:
            longitude = float(match.group(1))
            latitude = float(match.group(2))
            return (latitude, longitude)
            
        raise ValueError(f"Unknown format: {geography_data[:50]}...")

    except Exception as e:
        raise ValueError(f"Invalid geography format: {geography_data[:50]}...") from e