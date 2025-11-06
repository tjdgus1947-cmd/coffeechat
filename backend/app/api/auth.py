# File: tjdgus1947-cmd/coffeechat/coffeechat-db-ksh/backend/app/api/auth.py

from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import supabase # 👈 원래의 config 임포트 (supabase만 사용)

# 새로 추가된 임포트: 임베딩 서비스 직접 호출
from app.services.ml_service import generate_embedding
import uuid

router = APIRouter()

# --- Pydantic 스키마 정의 (원래 auth.py 파일에 없었으므로 다시 정의) ---
class MentorSignUp(BaseModel):
    email: EmailStr
    password: str
    name: str 
    company: Optional[str] = None   
    team: Optional[str] = None
    experienceYears: Optional[int] = 0
    topics: Optional[str] = None
    introduction: Optional[str] = None

class UserSignIn(BaseModel):
    email: EmailStr
    password: str
# --------------------------------------------------------------------

# --- 멘토 회원가입 (JSON 방식) ---
@router.post("/api/auth/register/mentor")
def sign_up_mentor(mentor_data: MentorSignUp):
    """
    멘토 회원가입 (JSON 방식)
    3개 테이블(auth.users, public.users, mentor_profiles)에 저장 및 AI 임베딩 생성
    """
    try:
        # 1. Supabase Auth (auth.users)에 유저 생성
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
        supabase.table('users').insert({
            "id": str(new_user_id), 
            "full_name": mentor_data.name,
            "role": "mentor"
        }).execute()
        
        # 3. mentor_profiles 테이블에 상세 프로필 생성
        career_info_text = f"회사: {mentor_data.company}, 직무: {mentor_data.team}, 경력: {mentor_data.experienceYears}년, 전문분야: {mentor_data.topics}, 소개: {mentor_data.introduction}"
        
        supabase.table('mentor_profiles').insert({
            "user_id": str(new_user_id), 
            "career_info": career_info_text 
        }).execute()
        
        # 4. ⭐️ AI 임베딩 생성 및 DB 업데이트 (WBS 4.1) ⭐️
        try:
            embedding_vector = generate_embedding(career_info_text)
            supabase.table('mentor_profiles') \
                     .update({"embedding": embedding_vector}) \
                     .eq("user_id", str(new_user_id)) \
                     .execute()
            print(f"✅ Mentor {new_user_id} embedding successfully generated and updated.")
        except Exception as e:
            print(f"⚠️ ERROR: Mentor embedding generation/update failed for {new_user_id}: {e}")
            pass # 임베딩 실패는 회원가입 실패로 이어지지 않음
                
        return response.user

    except Exception as e:
        # 400 Bad Request, 500 Internal Error 처리
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
    3개 테이블(auth.users, public.users, mentee_profiles)에 저장 및 AI 임베딩 생성
    """
    try:
        # 1. Supabase Auth (auth.users)에 유저 생성
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
        supabase.table('users').insert({
            "id": str(new_user_id), 
            "full_name": name,
            "role": "mentee"
        }).execute()
        
        # 3. mentee_profiles 테이블에 상세 프로필 생성
        mentee_profile_response = supabase.table('mentee_profiles').insert({
            "user_id": str(new_user_id), 
            "current_situation": situation,
            "career_goal": topics 
        }).execute()
        
        # 4. ⭐️ AI 임베딩 생성 및 DB 업데이트 (WBS 4.1) ⭐️
        text_to_embed = f"현재 상황: {situation}. 희망 진로: {topics}"
        try:
            embedding_vector = generate_embedding(text_to_embed)
            supabase.table('mentee_profiles') \
                     .update({"embedding": embedding_vector}) \
                     .eq("user_id", str(new_user_id)) \
                     .execute()
            print(f"✅ Mentee {new_user_id} embedding successfully generated and updated.")
        except Exception as e:
            print(f"⚠️ ERROR: Mentee embedding generation/update failed for {new_user_id}: {e}")
            pass # 임베딩 실패는 회원가입 실패로 이어지지 않음

        return response.user

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
        return response
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")