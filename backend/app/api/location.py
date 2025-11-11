# File: backend/app/api/location.py
# (WBS 5.2 - GIS 500 Internal Error 완전 해결 버전)
# 멘토/멘티 지도 뷰 동시 지원

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from app.core.config import supabase
from typing import List, Optional, Tuple
import re

# shapely 임포트 (없어도 동작하도록)
try:
    from shapely import wkb
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("shapely 미설치: WKB 파싱 없이 문자열/딕셔너리만 처리합니다.")

router = APIRouter()

# --- 스키마 ---
class LocationUpdateRequest(BaseModel):
    user_id: uuid.UUID
    role: str
    lon: float
    lat: float


class NearbyMentorsRequest(BaseModel):
    mentee_id: uuid.UUID
    radius_meters: int


class MapLocationInfo(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    role: str
    lat: float
    lon: float


class MapDataResponse(BaseModel):
    # 이름은 mentee/mentor지만 프론트 호환을 위해 '현재 사용자/다른 사용자'로 재활용
    mentee_location: Optional[MapLocationInfo] = None
    mentor_locations: List[MapLocationInfo] = []


# --- 헬퍼 함수 ---
def parse_location(location_data) -> Optional[Tuple[float, float]]:
    """
    다양한 형태의 location 값을 (lon, lat) 튜플로 파싱.
    지원: WKB(hex), 'POINT(lon lat)', {'lon','lat'} 또는 {'x','y'}
    """
    if not location_data:
        return None

    # 문자열 처리
    if isinstance(location_data, str):
        # 1) WKB hex
        if SHAPELY_AVAILABLE and re.match(r"^[0-9A-Fa-f]+$", location_data):
            try:
                point = wkb.loads(location_data, hex=True)
                return (point.x, point.y)
            except Exception as e:
                print(f"WKB 파싱 실패: {e}")

        # 2) WKT POINT(lon lat)
        match = re.search(
            r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", location_data, re.IGNORECASE
        )
        if match:
            return (float(match.group(1)), float(match.group(2)))

    # 딕셔너리 처리
    if isinstance(location_data, dict):
        if "lon" in location_data and "lat" in location_data:
            return (float(location_data["lon"]), float(location_data["lat"]))
        if "x" in location_data and "y" in location_data:
            return (float(location_data["x"]), float(location_data["y"]))

    print(f"⚠️ 알 수 없는 location 형식: {type(location_data)} - {location_data}")
    return None


# --- API 엔드포인트 ---
@router.post("/api/location/update")
def update_user_location(request: LocationUpdateRequest):
    try:
        if request.role == "mentor":
            table_name = "mentor_profiles"
        elif request.role == "mentee":
            table_name = "mentee_profiles"
        else:
            raise HTTPException(status_code=400, detail="Invalid role")

        location_point = f"POINT({request.lon} {request.lat})"

        response = (
            supabase.table(table_name)
            .update({"location": location_point})
            .eq("user_id", str(request.user_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found")

        return {"message": f"{request.role} {request.user_id}의 위치가 업데이트되었습니다."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 Location Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Location update failed: {str(e)}")


@router.post("/api/location/nearby-mentors")
def get_nearby_mentors(request: NearbyMentorsRequest):
    try:
        mentee_response = (
            supabase.table("mentee_profiles")
            .select("location")
            .eq("user_id", str(request.mentee_id))
            .limit(1)
            .execute()
        )

        if not mentee_response.data or not mentee_response.data[0].get("location"):
            raise HTTPException(status_code=404, detail="Mentee location not found")

        mentee_location = mentee_response.data[0]["location"]

        nearby_response = supabase.rpc(
            "nearby_mentors",
            {"mentee_location": mentee_location, "radius_meters": request.radius_meters},
        ).execute()

        return nearby_response.data

    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 Nearby Mentors Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# 멘토/멘티 역할에 따라 지도 데이터 반환
@router.get("/api/locations/map-data/{user_id}", response_model=MapDataResponse)
def get_all_map_locations(user_id: uuid.UUID):
    """
    지도 뷰에 필요한 '현재 사용자' 1명과 '다른 사용자들'의 위치 정보를 반환합니다.
    """
    try:
        response_data = MapDataResponse()

        # 1) 사용자 기본정보 조회
        user_query = (
            supabase.table("users")
            .select("role, full_name")
            .eq("id", str(user_id))
            .single()
            .execute()
        )
        if not user_query.data:
            raise HTTPException(status_code=404, detail="User not found")

        user_role = user_query.data["role"]
        user_name = user_query.data.get("full_name", "Unknown")

        # --- 2) 멘티 로그인 ---
        if user_role == "mentee":
            # 2a) 멘티 본인 위치
            try:
                mentee_query = (
                    supabase.table("mentee_profiles")
                    .select("id, user_id, location")
                    .eq("user_id", str(user_id))
                    .execute()
                )
                if mentee_query.data:
                    mentee = mentee_query.data[0]
                    parsed = parse_location(mentee.get("location"))
                    if parsed:
                        lon, lat = parsed
                        response_data.mentee_location = MapLocationInfo(
                            id=mentee["id"],
                            user_id=mentee["user_id"],
                            name=user_name,
                            role="mentee",
                            lat=lat,
                            lon=lon,
                        )
            except Exception as e:
                print(f"⚠️ 멘티(본인) 데이터 조회 오류: {str(e)}")

            # 2b) 모든 멘토 위치
            try:
                mentor_query = (
                    supabase.table("mentor_profiles")
                    .select("id, user_id, location")
                    .execute()
                )

                mentor_locations: List[MapLocationInfo] = []
                for mentor in mentor_query.data:
                    if not mentor.get("location"):
                        continue

                    try:
                        mentor_user = (
                            supabase.table("users")
                            .select("full_name, role")
                            .eq("id", str(mentor["user_id"]))
                            .single()
                            .execute()
                        )

                        parsed = parse_location(mentor.get("location"))
                        if parsed and mentor_user.data:
                            lon, lat = parsed
                            mentor_locations.append(
                                MapLocationInfo(
                                    id=mentor["id"],
                                    user_id=mentor["user_id"],
                                    name=mentor_user.data.get("full_name", "Unknown"),
                                    role=mentor_user.data.get("role", "mentor"),
                                    lat=lat,
                                    lon=lon,
                                )
                            )
                    except Exception as e:
                        print(f"⚠️ 멘토 {mentor['user_id']} 데이터 파싱 실패: {str(e)}")

                response_data.mentor_locations = mentor_locations
            except Exception as e:
                print(f"⚠️ 멘토 목록 조회 오류: {str(e)}")

        # --- 3) 멘토 로그인 ---
        elif user_role == "mentor":
            # 3a) 멘토 본인 위치
            try:
                mentor_query = (
                    supabase.table("mentor_profiles")
                    .select("id, user_id, location")
                    .eq("user_id", str(user_id))
                    .execute()
                )
                if mentor_query.data:
                    mentor = mentor_query.data[0]
                    parsed = parse_location(mentor.get("location"))
                    if parsed:
                        lon, lat = parsed
                        # 프론트 호환을 위해 mentee_location 필드에 본인(멘토) 저장
                        response_data.mentee_location = MapLocationInfo(
                            id=mentor["id"],
                            user_id=mentor["user_id"],
                            name=user_name,
                            role="mentor",
                            lat=lat,
                            lon=lon,
                        )
            except Exception as e:
                print(f"⚠️ 멘토(본인) 데이터 조회 오류: {str(e)}")

            # 3b) 모든 멘티 위치
            try:
                mentee_query = (
                    supabase.table("mentee_profiles")
                    .select("id, user_id, location")
                    .execute()
                )

                mentee_locations: List[MapLocationInfo] = []
                for mentee in mentee_query.data:
                    if not mentee.get("location"):
                        continue

                    try:
                        mentee_user = (
                            supabase.table("users")
                            .select("full_name, role")
                            .eq("id", str(mentee["user_id"]))
                            .single()
                            .execute()
                        )

                        parsed = parse_location(mentee.get("location"))
                        if parsed and mentee_user.data:
                            lon, lat = parsed
                            mentee_locations.append(
                                MapLocationInfo(
                                    id=mentee["id"],
                                    user_id=mentee["user_id"],
                                    name=mentee_user.data.get("full_name", "Unknown"),
                                    role=mentee_user.data.get("role", "mentee"),
                                    lat=lat,
                                    lon=lon,
                                )
                            )
                    except Exception as e:
                        print(f"⚠️ 멘티 {mentee['user_id']} 데이터 파싱 실패: {str(e)}")

                # 프론트 호환을 위해 mentor_locations에 멘티 목록 저장
                response_data.mentor_locations = mentee_locations
            except Exception as e:
                print(f"⚠️ 멘티 목록 조회 오류: {str(e)}")

        return response_data

    except Exception as e:
        print(f"🔥 Map Data Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Map data retrieval failed: {str(e)}"
        )
