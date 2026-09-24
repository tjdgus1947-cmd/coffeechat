# backend/app/api/location.py
"""
위치 API
- 위치 저장: 경도/위도 → PostGIS geography (WKT POINT)
- 주변 멘토: DB 함수 nearby_mentors (ST_DWithin + GiST 인덱스)
- 지도 데이터: 내 위치 + 상대 역할 사용자들의 위치

이전 버전은 ".eq() 버그 우회"라며 테이블 전체를 가져와 파이썬에서 사용자를 찾았다.
PK/UNIQUE 컬럼에 대한 eq 조회로 바꿔, 조회 1건이 행 1개만 읽도록 했다.
"""
import logging
import re
from typing import List, Literal, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import supabase
from .auth import get_current_user_id

logger = logging.getLogger(__name__)

try:
    from shapely import wkb
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("shapely 미설치: WKB 파싱 없이 문자열/딕셔너리만 처리합니다.")

router = APIRouter()


# --- 스키마 ---
class LocationUpdateRequest(BaseModel):
    role: Literal["mentor", "mentee"]
    lon: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)
    user_id: Optional[str] = None  # 하위 호환용, 사용하지 않음


class NearbyMentorsRequest(BaseModel):
    radius_meters: int = Field(..., gt=0, le=200_000)
    mentee_id: Optional[str] = None  # 하위 호환용, 사용하지 않음


class MapLocationInfo(BaseModel):
    id: str
    user_id: str
    name: str
    role: str
    lat: float
    lon: float


class MapDataResponse(BaseModel):
    mentee_location: Optional[MapLocationInfo] = None   # (이름은 기존 프론트 호환) 내 위치
    mentor_locations: List[MapLocationInfo] = []        # 상대 역할 사용자들의 위치


PROFILE_TABLE = {"mentor": "mentor_profiles", "mentee": "mentee_profiles"}


# --- 위치 파싱 헬퍼 함수 ---
def parse_location(location_data) -> Optional[Tuple[float, float]]:
    """
    다양한 형태의 location 값을 (lon, lat) 튜플로 파싱.
    """
    if not location_data: return None
    if isinstance(location_data, str):
        if SHAPELY_AVAILABLE and re.match(r"^[0-9A-Fa-f]+$", location_data):
            try:
                point = wkb.loads(location_data, hex=True)
                return (point.x, point.y) # (lon, lat)
            except HTTPException:
                raise
            except Exception:
                pass # WKT로 시도
        match = re.search(r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", location_data, re.IGNORECASE)
        if match:
            return (float(match.group(1)), float(match.group(2)))
    if isinstance(location_data, dict):
        if "lon" in location_data and "lat" in location_data:
            return (float(location_data["lon"]), float(location_data["lat"]))
        if "x" in location_data and "y" in location_data:
            return (float(location_data["x"]), float(location_data["y"]))
    print(f"⚠️ 알 수 없는 location 형식: {type(location_data)} - {str(location_data)[:50]}")
    return None


def _name_of(user_info) -> str:
    if isinstance(user_info, list) and user_info:
        user_info = user_info[0]
    if isinstance(user_info, dict):
        return user_info.get("full_name") or "Unknown"
    return "Unknown"


# --- API: 위치 업데이트 ---
@router.post("/api/location/update")
def update_user_location(
    request: LocationUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        response = (
            supabase.table(PROFILE_TABLE[request.role])
            .update({"location": f"POINT({request.lon} {request.lat})"})
            .eq("user_id", current_user_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found for location update")

        return {"message": "위치가 업데이트되었습니다."}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("위치 업데이트 실패: %s", e)
        raise HTTPException(status_code=500, detail="위치 업데이트 중 오류가 발생했습니다.")


# --- API: 주변 멘토 (RPC) ---
@router.post("/api/location/nearby-mentors")
def get_nearby_mentors(
    request: NearbyMentorsRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        me = (
            supabase.table("mentee_profiles")
            .select("location")
            .eq("user_id", current_user_id)
            .limit(1)
            .execute()
        )
        if not me.data or not me.data[0].get("location"):
            raise HTTPException(status_code=404, detail="Mentee location not found")

        nearby = supabase.rpc(
            "nearby_mentors",
            {"mentee_location": me.data[0]["location"], "radius_meters": request.radius_meters},
        ).execute()
        return nearby.data or []

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("주변 멘토 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail="주변 멘토 조회 중 오류가 발생했습니다.")


# --- API: 지도 데이터 ---
@router.get("/api/locations/map-data/{user_id}", response_model=MapDataResponse)
def get_all_map_locations(
    user_id: str,  # 하위 호환용 경로 변수, 사용하지 않음
    current_user_id: str = Depends(get_current_user_id),
):
    """
    내 위치와 상대 역할(멘티 → 멘토, 멘토 → 멘티) 사용자들의 위치를 반환한다.
    쿼리 3번: 내 정보 1건, 내 프로필 1건, 상대 역할 프로필 목록(이름 JOIN)
    """
    try:
        me = supabase.table("users").select("id, role, full_name").eq("id", current_user_id).limit(1).execute()
        if not me.data:
            raise HTTPException(status_code=404, detail="User not found")

        my_role = me.data[0]["role"]
        my_name = me.data[0].get("full_name") or "Unknown"
        other_role = "mentor" if my_role == "mentee" else "mentee"

        result = MapDataResponse()

        my_profile = (
            supabase.table(PROFILE_TABLE[my_role])
            .select("id, user_id, location")
            .eq("user_id", current_user_id)
            .limit(1)
            .execute()
        )
        if my_profile.data:
            parsed = parse_location(my_profile.data[0].get("location"))
            if parsed:
                lon, lat = parsed
                result.mentee_location = MapLocationInfo(
                    id=my_profile.data[0]["id"], user_id=current_user_id,
                    name=my_name, role=my_role, lat=lat, lon=lon,
                )

        others = (
            supabase.table(PROFILE_TABLE[other_role])
            .select("id, user_id, location, users(full_name)")
            .not_.is_("location", "null")
            .execute()
        )
        for row in others.data or []:
            parsed = parse_location(row.get("location"))
            if not parsed:
                continue
            lon, lat = parsed
            result.mentor_locations.append(MapLocationInfo(
                id=row["id"], user_id=row["user_id"], name=_name_of(row.get("users")),
                role=other_role, lat=lat, lon=lon,
            ))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("지도 데이터 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail="지도 데이터 조회 중 오류가 발생했습니다.")
