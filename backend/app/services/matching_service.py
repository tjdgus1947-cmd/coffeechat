# backend/app/services/matching_service.py
"""
자기소개(70%) + 거리(30%)를 결합한 AI 매칭 시스템
"""
from typing import List, Dict, Tuple
import math
import re  # ⭐️ 1. re 임포트 추가
from app.services.ml_service import calculate_match_score

# ⭐️ 2. shapely 임포트 시도
try:
    from shapely import wkb
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("⚠️ 경고: shapely 라이브러리가 없습니다. 'pip install shapely'를 실행하세요.")


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 좌표 간의 거리 계산 (Haversine 공식, km 단위)
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
    """
    if distance_km <= 0:
        return 100.0
    if distance_km >= max_distance:
        return 0.0
    
    score = 100 * (1 - distance_km / max_distance)
    return round(score, 2)


def calculate_final_match_score(
    text_embedding1: List[float],
    text_embedding2: List[float],
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    text_weight: float = 0.7,
    distance_weight: float = 0.3,
    max_distance: float = 50.0
) -> Dict[str, float]:
    """
    최종 매칭 점수 계산 (자기소개 70% + 거리 30%)
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


# ⭐️⭐️⭐️ 3. 여기가 핵심 수정 ⭐️⭐️⭐️
def extract_coordinates_from_geography(geography_data: str) -> Tuple[float, float]:
    """
    PostGIS Geography (WKB 또는 WKT)에서 위도/경도 추출
    
    Args:
        geography_data: PostGIS Point (WKB: "0101000..." 또는 WKT: "POINT(127 37)")
    
    Returns:
        Tuple[float, float]: (latitude, longitude)
    
    Raises:
        ValueError: 잘못된 형식의 geography 데이터인 경우
    """
    if not geography_data:
        raise ValueError("Location data is empty or None")

    try:
        # 1순위: WKB(16진수) 처리 (DB에서 직접 온 경우)
        if SHAPELY_AVAILABLE and re.match(r"^[0-9A-Fa-f]+$", geography_data):
            point = wkb.loads(geography_data, hex=True)
            # PostGIS는 (경도, 위도) 순서
            return (point.y, point.x) # (위도, 경도) 순서로 반환

        # 2순위: WKT(텍스트) 처리 (예: "POINT(127.0276 37.4979)")
        match = re.search(
            r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", geography_data, re.IGNORECASE
        )
        if match:
            longitude = float(match.group(1))
            latitude = float(match.group(2))
            return (latitude, longitude) # (위도, 경도) 순서로 반환
            
        # 둘 다 실패
        raise ValueError(f"Unknown format, not WKB or WKT: {geography_data[:50]}...")

    except Exception as e:
        raise ValueError(f"Invalid geography format: {geography_data[:50]}...") from e