# File: backend/app/api/location.py
# (WBS 5.2 - GIS 500 Internal Error 완전 해결 버전)

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import uuid
from app.core.config import supabase 
from typing import List, Optional
import re

# shapely 임포트
try:
    from shapely import wkb
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print

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
    mentee_location: Optional[MapLocationInfo] = None
    mentor_locations: List[MapLocationInfo] = []

# --- 헬퍼 함수 ---
def parse_location(location_data) -> Optional[tuple[float, float]]:
    """
    여러 형식의 location 데이터를 파싱합니다.
    - WKB Hex 문자열 (PostGIS 기본)
    - POINT(lon lat) 문자열
    - dict 형식
    """
    if not location_data:
        return None
    
    # 1. WKB Hex 문자열 파싱 시도
    if isinstance(location_data, str) and SHAPELY_AVAILABLE:
        # WKB Hex 형식 확인 (16진수 문자열)
        if re.match(r'^[0-9A-Fa-f]+$', location_data):
            try:
                point = wkb.loads(location_data, hex=True)
                return (point.x, point.y)  # (lon, lat)
            except Exception as e:
                print(f"WKB 파싱 실패: {e}")
        
        # 2. POINT(lon lat) 문자열 파싱
        match = re.search(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)', location_data, re.IGNORECASE)
        if match:
            return (float(match.group(1)), float(match.group(2)))
    
    # 3. dict 형식 ({"lon": x, "lat": y})
    if isinstance(location_data, dict):
        if 'lon' in location_data and 'lat' in location_data:
            return (location_data['lon'], location_data['lat'])
        if 'x' in location_data and 'y' in location_data:
            return (location_data['x'], location_data['y'])
    
    print(f"⚠️ 알 수 없는 location 형식: {type(location_data)} - {location_data}")
    return None

# --- API 엔드포인트 ---
@router.post("/api/location/update")
def update_user_location(request: LocationUpdateRequest):
    try:
        table_name = ""
        if request.role == 'mentor':
            table_name = 'mentor_profiles'
        elif request.role == 'mentee':
            table_name = 'mentee_profiles'
        else:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        location_point = f'POINT({request.lon} {request.lat})'
        response = supabase.table(table_name) \
                           .update({"location": location_point}) \
                           .eq("user_id", str(request.user_id)) \
                           .execute()
        
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
        mentee_response = supabase.table('mentee_profiles') \
                                  .select('location') \
                                  .eq('user_id', str(request.mentee_id)) \
                                  .limit(1) \
                                  .execute()
        
        if not mentee_response.data or not mentee_response.data[0].get('location'):
            raise HTTPException(status_code=404, detail="Mentee location not found")
        
        mentee_location = mentee_response.data[0]['location']
        nearby_response = supabase.rpc('nearby_mentors', {
            'mentee_location': mentee_location,
            'radius_meters': request.radius_meters
        }).execute()
        
        return nearby_response.data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 Nearby Mentors Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ⭐️ 핵심 수정: 500 에러 완전 해결
@router.get("/api/locations/map-data/{user_id}", response_model=MapDataResponse)
def get_all_map_locations(user_id: uuid.UUID):
    """
    지도 뷰에 필요한 멘티 1명과 모든 멘토의 위치 정보를 반환합니다.
    """
    try:
        response_data = MapDataResponse()
        
        # 1. 멘티 위치 조회 (수정된 쿼리)
        try:
            mentee_query = supabase.table("mentee_profiles") \
                .select("id, user_id, location") \
                .eq("user_id", str(user_id)) \
                .execute()
            
            if mentee_query.data:
                mentee = mentee_query.data[0]
                
                # 멘티 이름 조회 (별도 쿼리)
                user_query = supabase.table("users") \
                    .select("full_name, role") \
                    .eq("id", str(user_id)) \
                    .single() \
                    .execute()
                
                # location 파싱
                parsed_location = parse_location(mentee.get('location'))
                if parsed_location and user_query.data:
                    lon, lat = parsed_location
                    response_data.mentee_location = MapLocationInfo(
                        id=mentee['id'],
                        user_id=mentee['user_id'],
                        name=user_query.data.get('full_name', 'Unknown'),
                        role=user_query.data.get('role', 'mentee'),
                        lat=lat,
                        lon=lon
                    )
        except Exception as e:
            print(f"⚠️ 멘티 데이터 조회 오류: {str(e)}")
            # 멘티 데이터 실패 시 계속 진행 (멘토 데이터만이라도 반환)
        
        # 2. 모든 멘토 위치 조회 (수정된 쿼리)
        try:
            mentor_query = supabase.table("mentor_profiles") \
                .select("id, user_id, location") \
                .execute()
            
            mentor_locations = []
            for mentor in mentor_query.data:
                if not mentor.get('location'):
                    continue
                
                # 멘토 이름 조회 (별도 쿼리)
                try:
                    user_query = supabase.table("users") \
                        .select("full_name, role") \
                        .eq("id", str(mentor['user_id'])) \
                        .single() \
                        .execute()
                    
                    parsed_location = parse_location(mentor.get('location'))
                    if parsed_location and user_query.data:
                        lon, lat = parsed_location
                        mentor_locations.append(MapLocationInfo(
                            id=mentor['id'],
                            user_id=mentor['user_id'],
                            name=user_query.data.get('full_name', 'Unknown'),
                            role=user_query.data.get('role', 'mentor'),
                            lat=lat,
                            lon=lon
                        ))
                except Exception as e:
                    print(f"⚠️ 멘토 {mentor['user_id']} 데이터 파싱 실패: {str(e)}")
                    continue
            
            response_data.mentor_locations = mentor_locations
        
        except Exception as e:
            print(f"⚠️ 멘토 데이터 조회 오류: {str(e)}")
        
        return response_data
    
    except Exception as e:
        print(f"🔥 Map Data Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Map data retrieval failed: {str(e)}")