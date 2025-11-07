# backend/app/api/auth.py
# (ERD v2 최종 수정본: 3-table insert 버그 수정)

from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import supabase
from gotrue.errors import AuthApiError
from gotrue.types import User
import uuid

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        response = supabase.auth.get_user(token)
        user = response.user
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user
    
    except AuthApiError as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {e.message}")
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")


def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return str(current_user.id)

# --- 멘토 회원가입 (JSON 방식) ---
class MentorSignUp(BaseModel):
    email: EmailStr
    password: str
    name: str 
    company: Optional[str] = None   
    team: Optional[str] = None
    experienceYears: Optional[int] = 0
    topics: Optional[str] = None
    introduction: Optional[str] = None

@router.post("/api/auth/register/mentor")
def sign_up_mentor(mentor_data: MentorSignUp):
    """
    멘토 회원가입 (JSON 방식)
    새로운 ERD에 맞춰 3개 테이블(auth.users[cite: image_075159.png], public.users, mentor_profiles[cite: setup_v2.sql])에 저장
    """
    try:
        # 1. Supabase Auth (auth.users[cite: image_075159.png])에 유저 생성
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
            
        # 2. (새로운 ERD) public.users 테이블[cite: setup_v2.sql]에 공통 프로필 생성
        user_profile_response = supabase.table('users').insert({
            "id": str(new_user_id), 
            "full_name": mentor_data.name,
            "role": "mentor"
        }).execute()
        
        if not user_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create user profile in public.users")
        
        # 3. (새로운 ERD) mentor_profiles[cite: setup_v2.sql] 테이블에 상세 프로필 생성
        career_info_text = f"회사: {mentor_data.company}, 직무: {mentor_data.team}, 경력: {mentor_data.experienceYears}년, 전문분야: {mentor_data.topics}, 소개: {mentor_data.introduction}"
        
        # 🚨 (수정) ERD에 맞게 'full_name' 컬럼 제거
        mentor_profile_response = supabase.table('mentor_profiles').insert({
            "user_id": str(new_user_id), 
            "career_info": career_info_text 
        }).execute()
            
        if not mentor_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentor_profiles[cite: setup_v2.sql] entry")
                
        return response.user

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
    proofFile: Optional[UploadFile] = File(None) 
):
    """
    멘티 회원가입 (FormData 방식)
    새로운 ERD에 맞춰 3개 테이블(auth.users[cite: image_075159.png], public.users, mentee_profiles[cite: setup_v2.sql])에 저장
    """
    try:
        # 1. Supabase Auth (auth.users[cite: image_075159.png])에 유저 생성
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

        # 2. (새로운 ERD) public.users 테이블[cite: setup_v2.sql]에 공통 프로필 생성
        user_profile_response = supabase.table('users').insert({
            "id": str(new_user_id), 
            "full_name": name,
            "role": "mentee"
        }).execute()
        
        if not user_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create user profile in public.users")

        # 3. (새로운 ERD) mentee_profiles[cite: setup_v2.sql] 테이블에 상세 프로필 생성
        # 🚨 (수정) ERD에 맞게 'full_name' 컬럼 제거
        mentee_profile_response = supabase.table('mentee_profiles').insert({
            "user_id": str(new_user_id), 
            "current_situation": situation,
            "career_goal": topics 
        }).execute()

        if not mentee_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentee_profiles[cite: setup_v2.sql] entry")

        return response.user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 로그인 (공통) ---
class UserSignIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/login")
def sign_in(user_data: UserSignIn):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")