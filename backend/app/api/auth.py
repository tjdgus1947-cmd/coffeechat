# backend/app/api/auth.py
from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import supabase
from app.services.ml_service import generate_embedding
import uuid
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gotrue.errors import AuthApiError
from gotrue.types import User


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    JWT 토큰을 검증하고 User 객체를 반환합니다.
    """
    try:
        print(f"🔐 토큰 검증 시도: {token[:20]}...")  # 👈 디버깅 로그
        
        # Supabase에서 토큰으로 사용자 정보 가져오기
        response = supabase.auth.get_user(token)
        user = response.user

        if not user:
            print("❌ 토큰 검증 실패: user 객체가 None")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        print(f"✅ 토큰 검증 성공: user_id={user.id}")
        return user

    except AuthApiError as e:
        print(f"❌ Supabase Auth 오류: {e.message}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {e.message}")

    except Exception as e:
        print(f"❌ 예상치 못한 오류: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")


def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
    """
    현재 인증된 사용자의 ID를 반환합니다.
    """
    if not current_user:
        print("❌ current_user가 None입니다.")
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = str(current_user.id)
    print(f"✅ 사용자 ID 추출 성공: {user_id}")
    return user_id


# --- Pydantic 스키마 정의 ---
class MentorSignUp(BaseModel):
    email: EmailStr
    password: str
    name: str 
    company: Optional[str] = None   
    team: Optional[str] = None
    experienceYears: Optional[int] = 0
    topics: Optional[str] = None
    introduction: Optional[str] = None
    # 🆕 위치 정보 추가
    latitude: float
    longitude: float

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

# --- 멘토 회원가입 (JSON 방식) ---
@router.post("/api/auth/register/mentor")
def sign_up_mentor(mentor_data: MentorSignUp):
    """
    멘토 회원가입 (JSON 방식)
    """
    try:
        # 1. Supabase Auth에 사용자 생성
        response = supabase.auth.sign_up({
            "email": mentor_data.email,
            "password": mentor_data.password,
            "options": {
                "data": {
                    "role": "mentor", 
                    "full_name": mentor_data.name 
                }
            }
        })
        
        if not response.user:
             raise HTTPException(status_code=400, detail="User already exists or sign up failed")

        new_user_id = response.user.id
            
        # 2. public.users 테이블에 공통 프로필 생성
        user_profile_response = supabase.table('users').insert({
            "id": str(new_user_id), 
            "full_name": mentor_data.name,
            "role": "mentor"
        }).execute()
        
        if not user_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create user profile in public.users")
        

      
        career_info_text = f"회사: {mentor_data.company}, 직무: {mentor_data.team}, 경력: {mentor_data.experienceYears}년, 전문분야: {mentor_data.topics}, 소개: {mentor_data.introduction}"
        
        # 4. 🆕 PostGIS Point 형식으로 위치 생성 (경도, 위도 순서 주의!)
        location_point = f"POINT({mentor_data.longitude} {mentor_data.latitude})"
        
        # 5. ⭐️ AI 임베딩 생성
        try:
            embedding_vector = generate_embedding(career_info_text)
        except Exception as e:
            print(f"⚠️ Embedding generation failed: {e}")
            embedding_vector = None
        
        # 6. mentor_profiles 테이블에 상세 프로필 생성 (임베딩 + 위치 포함)
        mentor_profile_response = supabase.table('mentor_profiles').insert({
            "user_id": str(new_user_id), 
            "career_info": career_info_text,
            "location": location_point,
            "embedding": embedding_vector
        }).execute()
            
        if not mentor_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentor_profiles entry")
        
        print(f"✅ Mentor {new_user_id} registered with embedding and location.")
                
        return {
            "user": response.user,
            "message": "멘토 회원가입 완료. 매칭 시스템이 자동 설정되었습니다.",
            "location": {
                "latitude": mentor_data.latitude,
                "longitude": mentor_data.longitude
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 멘티 회원가입 (FormData 방식) ---
@router.post("/api/auth/register/mentee")
def sign_up_mentee(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...), 
    situation: Optional[str] = Form(None), 
    topics: Optional[str] = Form(None),
    # 🆕 위치 정보 추가
    latitude: float = Form(...),
    longitude: float = Form(...),
    proofFile: Optional[UploadFile] = File(None) 
):
    """
    멘티 회원가입 (FormData 방식)
    """
    try:
        # 1. Supabase Auth에 사용자 생성
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "role": "mentee",
                    "full_name": name
                }
            }
        })

        if not response.user:
             raise HTTPException(status_code=400, detail="User already exists or sign up failed")

        new_user_id = response.user.id

        # 2. public.users 테이블에 공통 프로필 생성
        user_profile_response = supabase.table('users').insert({
            "id": str(new_user_id), 
            "full_name": name,
            "role": "mentee"
        }).execute()
        
        if not user_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create user profile in public.users")

        # 3. mentee_profiles 테이블에 상세 프로필 생성
        
        # 3. career_goal 텍스트 생성
        text_to_embed = f"현재 상황: {situation}. 희망 진로: {topics}"
        
        # 4. 🆕 PostGIS Point 형식으로 위치 생성
        location_point = f"POINT({longitude} {latitude})"
        embedding_vector = None
        # 5. ⭐️ AI 임베딩 생성
        try:
            embedding_vector = generate_embedding(text_to_embed)
        except Exception as e:
            print(f"⚠️ Embedding generation failed: {e}")
            
        
        # 6. mentee_profiles 테이블에 상세 프로필 생성 (임베딩 + 위치 포함)
        
        mentee_profile_response = supabase.table('mentee_profiles').insert({
            "user_id": str(new_user_id), 
            "current_situation": situation,
            "career_goal": topics,
            "location": location_point,
            "embedding": embedding_vector
        }).execute()
        
        print(f"✅ Mentee {new_user_id} registered with embedding and location.")

        if not mentee_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentee_profiles entry")

       
        return {
            "user": response.user,
            "message": "멘티 회원가입 완료. 매칭 시스템이 자동 설정되었습니다.",
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 로그인 (공통) ---
@router.post("/api/auth/login")
def sign_in(user_data: UserSignIn):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        print(f"✅ 로그인 성공: {response.user.id if response.user else 'No user'}")
        return response
    except Exception as e:
        print(f"❌ 로그인 실패: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")