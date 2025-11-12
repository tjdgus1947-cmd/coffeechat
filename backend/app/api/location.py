# backend/app/api/location.py
# (WBS 5.2 - .eq() 버그를 Python으로 우회하는 최종 해결 버전)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from app.core.config import supabase
from typing import List, Optional, Tuple
import re
import unicodedata  # ⭐️ 1. unicodedata 임포트 (ID 정규화용)

# shapely 임포트 (기존과 동일)
try:
    from shapely import wkb
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("shapely 미설치: WKB 파싱 없이 문자열/딕셔너리만 처리합니다.")

router = APIRouter()

# --- 스키마 (기존과 동일) ---
class LocationUpdateRequest(BaseModel):
    user_id: str # ⭐️ uuid.UUID -> str로 변경 (공식 클라이언트와 맞춤)
    role: str
    lon: float
    lat: float

class NearbyMentorsRequest(BaseModel):
    mentee_id: str # ⭐️ uuid.UUID -> str
    radius_meters: int

class MapLocationInfo(BaseModel):
    id: str # ⭐️ uuid.UUID -> str
    user_id: str # ⭐️ uuid.UUID -> str
    name: str
    role: str
    lat: float
    lon: float

class MapDataResponse(BaseModel):
    mentee_location: Optional[MapLocationInfo] = None
    mentor_locations: List[MapLocationInfo] = []

# --- ⭐️ 2. matching.py에서 헬퍼 함수 2개 복사 ---

def get_clean_user_id(user_id: str) -> str:
    """모든 user_id 문자열을 정규화하고 공백을 제거합니다."""
    if not user_id:
        return None
    return unicodedata.normalize('NFC', user_id).strip()

def find_profile_in_list(response_data: list, user_id_str: str, id_key: str = "user_id"):
    """DB 응답(리스트)에서 Python으로 user_id를 찾아 프로필을 반환합니다."""
    if not response_data:
        return None
        
    for profile in response_data:
        db_user_id = profile.get(id_key) # id_key (user_id 또는 id)로 검색
        if db_user_id:
            db_id_clean = get_clean_user_id(db_user_id)
            if db_id_clean == user_id_str:
                return profile # 찾았으면 반환
    return None # 못 찾으면 None

# --- 헬퍼 함수 (기존과 동일) ---
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

# --- API 엔드포인트 (⭐️ 3. .eq() 로직 수정) ---

@router.post("/api/location/update")
def update_user_location(request: LocationUpdateRequest):
    try:
        user_id_str = get_clean_user_id(request.user_id) # ⭐️ ID 정규화
        if not user_id_str:
            raise HTTPException(status_code=400, detail="Invalid User ID")
            
        table_name = "mentor_profiles" if request.role == "mentor" else "mentee_profiles"
        location_point = f"POINT({request.lon} {request.lat})"

        response = (
            supabase.table(table_name)
            .update({"location": location_point})
            .eq("user_id", user_id_str) # ⭐️ .eq()는 update/post에선 잘 작동함
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found for location update")

        return {"message": f"{request.role} {user_id_str}의 위치가 업데이트되었습니다."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 Location Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Location update failed: {str(e)}")


@router.post("/api/location/nearby-mentors")
def get_nearby_mentors(request: NearbyMentorsRequest):
    try:
        mentee_id_str = get_clean_user_id(request.mentee_id) # ⭐️ ID 정규화
        
        # ⭐️ .eq() 대신 Python 검색
        all_mentees_resp = supabase.table("mentee_profiles").select("user_id, location").execute()
        mentee_profile = find_profile_in_list(all_mentees_resp.data, mentee_id_str)

        if not mentee_profile or not mentee_profile.get("location"):
            raise HTTPException(status_code=404, detail="Mentee location not found")

        mentee_location = mentee_profile["location"] # "01010..." WKB 바이너리

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


# ⭐️ 4. "지도 뷰" API (핵심 수정) ⭐️
@router.get("/api/locations/map-data/{user_id}", response_model=MapDataResponse)
def get_all_map_locations(user_id: str): # ⭐️ uuid.UUID -> str
    """
    지도 뷰에 필요한 '현재 사용자' 1명과 '다른 사용자들'의 위치 정보를 반환합니다.
    (.eq() 버그 수정됨)
    """
    try:
        user_id_str = get_clean_user_id(user_id) # ⭐️ ID 정규화
        response_data = MapDataResponse()

        # 1) 사용자 기본정보 조회 (⭐️ .eq() 대신 Python 검색)
        all_users_resp = supabase.table("users").select("id, role, full_name").execute()
        current_user = find_profile_in_list(all_users_resp.data, user_id_str, id_key="id") # ⭐️ id_key 사용
        
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        user_role = current_user["role"]
        user_name = current_user.get("full_name", "Unknown")

        # --- 2) DB에서 프로필 정보 미리 다 가져오기 ---
        all_mentee_profiles = supabase.table("mentee_profiles").select("id, user_id, location").execute().data
        all_mentor_profiles = supabase.table("mentor_profiles").select("id, user_id, location").execute().data

        # --- 3) 멘티 로그인 ---
        if user_role == "mentee":
            # 3a) 멘티 본인 위치 (Python 검색)
            mentee = find_profile_in_list(all_mentee_profiles, user_id_str)
            if mentee:
                parsed = parse_location(mentee.get("location"))
                if parsed:
                    lon, lat = parsed
                    response_data.mentee_location = MapLocationInfo(
                        id=mentee["id"], user_id=mentee["user_id"], name=user_name,
                        role="mentee", lat=lat, lon=lon,
                    )

            # 3b) 모든 멘토 위치 (전체 목록 순회)
            mentor_locations: List[MapLocationInfo] = []
            for mentor in all_mentor_profiles:
                if not mentor.get("location"): continue
                
                mentor_user = find_profile_in_list(all_users_resp.data, mentor["user_id"], id_key="id")
                parsed = parse_location(mentor.get("location"))
                
                if parsed and mentor_user:
                    lon, lat = parsed
                    mentor_locations.append(
                        MapLocationInfo(
                            id=mentor["id"], user_id=mentor["user_id"],
                            name=mentor_user.get("full_name", "Unknown"),
                            role=mentor_user.get("role", "mentor"),
                            lat=lat, lon=lon,
                        )
                    )
            response_data.mentor_locations = mentor_locations

        # --- 4) 멘토 로그인 ---
        elif user_role == "mentor":
            # 4a) 멘토 본인 위치 (Python 검색)
            mentor = find_profile_in_list(all_mentor_profiles, user_id_str)
            if mentor:
                parsed = parse_location(mentor.get("location"))
                if parsed:
                    lon, lat = parsed
                    response_data.mentee_location = MapLocationInfo(
                        id=mentor["id"], user_id=mentor["user_id"], name=user_name,
                        role="mentor", lat=lat, lon=lon,
                    )
            
            # 4b) 모든 멘티 위치 (전체 목록 순회)
            mentee_locations: List[MapLocationInfo] = []
            for mentee in all_mentee_profiles:
                if not mentee.get("location"): continue

                mentee_user = find_profile_in_list(all_users_resp.data, mentee["user_id"], id_key="id")
                parsed = parse_location(mentee.get("location"))
                
                if parsed and mentee_user:
                    lon, lat = parsed
                    mentee_locations.append(
                        MapLocationInfo(
                            id=mentee["id"], user_id=mentee["user_id"],
                            name=mentee_user.get("full_name", "Unknown"),
                            role=mentee_user.get("role", "mentee"),
                            lat=lat, lon=lon,
                        )
                    )
            response_data.mentor_locations = mentee_locations

        return response_data

    except Exception as e:
        print(f"🔥 Map Data Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Map data retrieval failed: {str(e)}"
        )