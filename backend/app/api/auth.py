# backend/app/api/auth.py
# (최종 수정본: 멘토/멘티 API 분리)

from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import supabase

router = APIRouter()

# --- 멘토 회원가입 (JSON 방식) ---

# 1. 멘토 폼(JSON)에 맞는 Pydantic 모델
class MentorSignUp(BaseModel):
    email: EmailStr
    password: str
    name: str # 👈 'full_name' 대신 'name'
    company: Optional[str] = None
    team: Optional[str] = None
    experienceYears: Optional[int] = 0
    topics: Optional[str] = None
    introduction: Optional[str] = None

@router.post("/api/auth/register/mentor")
def sign_up_mentor(mentor_data: MentorSignUp):
    """
    멘토 회원가입 (JSON 방식)
    wbs.md 3.1[cite: wbs.md], 3.2[cite: wbs.md]
    """
    try:
        # 1. Supabase Auth로 회원가입
        response = supabase.auth.sign_up({
            "email": mentor_data.email,
            "password": mentor_data.password,
            "options": {
                "data": {
                    "role": "mentor", # 👈 역할(role) 저장
                    "full_name": mentor_data.name # 👈 auth.users[cite: image_075159.png]에도 이름 저장
                }
            }
        })
        
        if not response.user:
             raise HTTPException(status_code=400, detail="User already exists or sign up failed")

        new_user_id = response.user.id
            
        # 2. mentor_profiles 테이블[cite: image_9f2523.png]에 프로필 생성
        # (AI 임베딩에 사용할 career_info를 조합)
        career_info_text = f"""
        회사: {mentor_data.company}, 
        직무: {mentor_data.team}, 
        경력: {mentor_data.experienceYears}년, 
        전문분야: {mentor_data.topics}, 
        소개: {mentor_data.introduction}
        """
        
        profile_response = supabase.table('mentor_profiles').insert({
            "id": str(new_user_id),
            "full_name": mentor_data.name,
            "career_info": career_info_text # 👈 AI 매칭용 원본 텍스트
        }).execute()
            
        if not profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentor profile")
                
        return response.user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 멘티 회원가입 (FormData 방식) ---

@router.post("/api/auth/register/mentee")
def sign_up_mentee(
    # 멘티 폼(FormData)의 필드와 1:1 매칭
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...), # 👈 'full_name' 대신 'name'
    situation: Optional[str] = Form(None), # 👈 'current_situation' 대신 'situation'
    topics: Optional[str] = Form(None),      # 👈 'career_goal' 대신 'topics'
    proofFile: Optional[UploadFile] = File(None) # 👈 'proof_file' 대신 'proofFile'
):
    """
    멘티 회원가입 (FormData 방식, 파일 업로드 포함)
    wbs.md 3.1[cite: wbs.md], 3.2[cite: wbs.md], 3.3[cite: wbs.md]
    """
    
    # (참고: proofFile을 Supabase Storage에 업로드하는 로직은 
    #  wbs.md 3.3[cite: wbs.md]에 따라 별도 API로 분리하는 것이 좋습니다. 
    #  지금은 텍스트만 저장하여 500 에러[cite: image_1cf5c0.png]를 해결합니다.)
    
    # print(f"Received file: {proofFile.filename}") # 파일 수신 확인 (터미널)

    try:
        # 1. Supabase Auth로 회원가입
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "role": "mentee", # 👈 역할(role) 저장
                    "full_name": name
                }
            }
        })

        if not response.user:
             raise HTTPException(status_code=400, detail="User already exists or sign up failed")

        new_user_id = response.user.id

        # 2. mentee_profiles 테이블[cite: image_9f251a.png]에 프로필 생성
        profile_response = supabase.table('mentee_profiles').insert({
            "id": str(new_user_id),
            "full_name": name,
            "current_situation": situation, # 👈 DB 컬럼명과 일치
            "career_goal": topics           # 👈 'topics'를 'career_goal' 컬럼에 저장
        }).execute()

        if not profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentee profile")

        return response.user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 로그인 (공통) ---

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/login")
def sign_in(user_data: UserSignIn):
    """
    Supabase Auth를 사용하여 로그인을 수행하고 JWT 토큰을 반환합니다.
    (wbs.md 3.1)[cite: wbs.md]
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")