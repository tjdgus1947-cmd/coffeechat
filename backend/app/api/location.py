# backend/app/api/location.py
# (ERD v2 수정본)

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import uuid
from app.core.config import supabase 

router = APIRouter()

class LocationUpdateRequest(BaseModel):
    user_id: uuid.UUID # 👈 public.users.id
    role: str 
    lon: float 
    lat: float 

class NearbyMentorsRequest(BaseModel):
    mentee_id: uuid.UUID # 👈 public.users.id
    radius_meters: int 

@router.post("/api/location/update")
def update_user_location(request: LocationUpdateRequest):
    """
    (수정됨) 멘토 또는 멘티의 위치 정보를 'user_id' 기준으로 DB에 업데이트합니다.
    """
    try:
        rpc_function_name = ""
        rpc_params = {}
        
        # 🚨 (수정된 핵심 로직)
        # setup_v2.sql[cite: setup_v2.sql]의 함수가 'profile_id'를 받도록 수정되었으므로,
        # 'user_id'로 'profile_id'를 조회해야 합니다. (더 간단하게 함수를 수정하겠습니다.)
        
        table_name = ""
        if request.role == 'mentor':
            table_name = 'mentor_profiles'
        elif request.role == 'mentee':
            table_name = 'mentee_profiles'
        else:
            raise HTTPException(status_code=400, detail="Invalid role")

        # 🚨 (수정된 핵심 로직)
        # SQL 함수를 호출하는 대신, 'user_id'로 직접 UPDATE
        response = supabase.table(table_name) \
                           .update({"location": f'POINT({request.lon} {request.lat})'}) \
                           .eq("user_id", str(request.user_id)) \
                           .select() \
                           .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found or update failed")

        return {"message": f"{request.role} {request.user_id}의 위치가 업데이트되었습니다."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/location/nearby-mentors")
def get_nearby_mentors(request: NearbyMentorsRequest):
    """
    (수정됨) 멘티의 'user_id'를 기준으로 반경 내의 멘토를 검색합니다.
    """
    try:
        # 1. 멘티의 위치(location)를 'user_id' 기준으로 조회
        mentee_response = supabase.table('mentee_profiles') \
                                  .select('location') \
                                  .eq('user_id', request.mentee_id) \
                                  .limit(1) \
                                  .execute()
        
        if not mentee_response.data or not mentee_response.data[0].get('location'):
            raise HTTPException(status_code=404, detail="Mentee location not found. Please update location first.")
        
        mentee_location = mentee_response.data[0]['location']
        
        # 2. 'nearby_mentors' SQL 함수 호출 (이 함수는 setup_v2.sql[cite: setup_v2.sql]에서 이미 수정됨)
        nearby_response = supabase.rpc('nearby_mentors', {
            'mentee_location': mentee_location,
            'radius_meters': request.radius_meters
        }).execute()

        return nearby_response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))