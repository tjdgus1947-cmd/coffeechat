# backend/app/api/location.py

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import uuid
# 4단계에서 설정한 config.py에서 supabase 클라이언트를 가져옵니다.
from app.core.config import supabase 

router = APIRouter()

class LocationUpdateRequest(BaseModel):
    user_id: uuid.UUID
    role: str # 'mentor' 또는 'mentee'
    lon: float # 경도 (Longitude)
    lat: float # 위도 (Latitude)

class NearbyMentorsRequest(BaseModel):
    mentee_id: uuid.UUID
    radius_meters: int # 검색 반경 (미터) (예: 5000 = 5km)

@router.post("/api/location/update")
def update_user_location(request: LocationUpdateRequest):
    """
    멘토 또는 멘티의 위치 정보를 DB에 업데이트합니다.
    (20단계에서 만든 SQL 함수 호출)
    """
    try:
        rpc_function_name = ""
        rpc_params = {}

        if request.role == 'mentor':
            rpc_function_name = 'update_mentor_location'
            rpc_params = {'mentor_id': str(request.user_id), 'lon': request.lon, 'lat': request.lat}
        elif request.role == 'mentee':
            rpc_function_name = 'update_mentee_location'
            rpc_params = {'mentee_id': str(request.user_id), 'lon': request.lon, 'lat': request.lat}
        else:
            raise HTTPException(status_code=400, detail="Invalid role")

        # 20단계에서 만든 SQL 함수를 RPC(Remote Procedure Call)로 호출
        supabase.rpc(rpc_function_name, rpc_params).execute()
        
        return {"message": f"{request.role} {request.user_id}의 위치가 업데이트되었습니다."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/location/nearby-mentors")
def get_nearby_mentors(request: NearbyMentorsRequest):
    """
    멘티의 위치를 기준으로 반경 내의 멘토를 검색합니다.
    (19단계에서 만든 SQL 함수 호출)
    """
    try:
        # 1. 멘티의 위치(location)를 DB에서 먼저 조회합니다.
        mentee_response = supabase.table('mentee_profiles').select('location').eq('id', request.mentee_id).single().execute()
        
        if not mentee_response.data or not mentee_response.data.get('location'):
            raise HTTPException(status_code=404, detail="Mentee location not found. Please update location first.")
        
        mentee_location = mentee_response.data['location']
        
        # 2. 19단계에서 만든 'nearby_mentors' SQL 함수를 호출
        nearby_response = supabase.rpc('nearby_mentors', {
            'mentee_location': mentee_location,
            'radius_meters': request.radius_meters
        }).execute()

        return nearby_response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))