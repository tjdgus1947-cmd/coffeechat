# backend/app/api/auth.py

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, EmailStr
# 4단계에서 설정한 config.py에서 supabase 클라이언트를 가져옵니다.
from app.core.config import supabase

router = APIRouter()

# 9.2 Pydantic 스키마 정의 (데이터 모델)
class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    role: str # 'mentor' 또는 'mentee' (WBS 3.2)
    full_name: str # 프로필에 사용할 이름

# (로그인 API용 스키마도 미리 추가)
class UserSignIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/register")
def sign_up(user_data: UserSignUp):
    """
    Supabase Auth를 사용하여 새 사용자를 등록합니다.
    (auth.users의 raw_user_meta_data에 'role'도 함께 저장)
    """
    try:
        # 1. Supabase Auth로 회원가입
        # 'options'를 추가하여 raw_user_meta_data에 "역할"과 "이름"을 저장합니다.
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "role": user_data.role,        # 👈 멘토/멘티 역할 저장
                    "full_name": user_data.full_name # 👈 (선택) 이름도 함께 저장
                }
            }
        })
        
        # 2. 회원가입 성공 시, 반환된 user 객체 확인
        if response.user and response.user.id:
            new_user_id = response.user.id
            
            # 3. 역할(role)에 따라 멘토 또는 멘티 프로필 생성 (WBS 3.2)
            table_name = ""
            profile_data = {}
            
            if user_data.role == 'mentor':
                table_name = 'mentor_profiles'
                profile_data = {
                    "id": str(new_user_id), # auth.users의 id와 동일하게 설정
                    "full_name": user_data.full_name
                }
            elif user_data.role == 'mentee':
                table_name = 'mentee_profiles'
                profile_data = {
                    "id": str(new_user_id),
                    "full_name": user_data.full_name
                }
            else:
                # (이론상 UserSignUp 스키마에서 role을 검증할 수도 있습니다)
                raise HTTPException(status_code=400, detail="Invalid role specified")
            
            # 4. 해당 프로필 테이블에 데이터 삽입
            profile_response = supabase.table(table_name).insert(profile_data).execute()
            
            if profile_response.data:
                print(f"Successfully created profile for {user_data.role}: {new_user_id}")
                # 9단계에서 만든 response.user 객체를 그대로 반환해줍니다.
                return response.user
            else:
                # (롤백 로직이 필요할 수 있으나, MVP에서는 에러 리포트로 대체)
                raise HTTPException(status_code=500, detail="Failed to create user profile")

        elif response.user is None and response.session is None:
             raise HTTPException(status_code=400, detail="User already exists")
        else:
             raise HTTPException(status_code=500, detail=str(response.model_dump()))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/auth/login")
def sign_in(user_data: UserSignIn):
    """
    Supabase Auth를 사용하여 로그인을 수행하고 JWT 토큰을 반환합니다.
    (WBS 3.1)
    """
    try:
        # Supabase의 내장 로그인 함수를 호출
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        # Supabase가 JWT 토큰이 포함된 세션(session) 정보를 반환합니다.
        return response

    except Exception as e:
        # Supabase에서 인증 실패 시 에러가 발생합니다.
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")

# (wbs_detail.md의 '현재 사용자' API 예시)
# @router.get("/api/auth/me")
# def get_current_user(token: str = Depends(oauth2_scheme)): # (FastAPI 보안 설정 필요)
#     try:
#         # 토큰(JWT)을 Supabase에 보내 유저 정보를 확인합니다.
#         user_response = supabase.auth.get_user(token)
#         return user_response.user
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token")