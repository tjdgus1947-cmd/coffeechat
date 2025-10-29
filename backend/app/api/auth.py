# backend/app/api/auth.py

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, EmailStr
# 4단계에서 설정한 config.py에서 supabase 클라이언트를 가져옵니다.
from app.core.config import supabase

router = APIRouter()

# 9.2 Pydantic 스키마 정의
class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    role: str # 'mentor' 또는 'mentee' (WBS 3.2 멘토/멘티 선택)
    full_name: str # 프로필에 사용할 이름
    
    # (프로필 등록에 필요한 추가 정보도 여기에 포함할 수 있습니다)
    # career_info: str | None = None
    # current_situation: str | None = None

@router.post("/api/auth/register")
def sign_up(user_data: UserSignUp):
    """
    Supabase Auth를 사용하여 새 사용자를 등록합니다. (WBS 3.1)
    """
    try:
        # 1. Supabase Auth로 회원가입
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })
        
        # 2. 회원가입 성공 시, 반환된 user 객체 확인
        if response.user and response.user.id:
            new_user_id = response.user.id
            
            # 3. 역할(role)에 따라 멘토 또는 멘티 프로필 생성 (WBS 3.2)
            #    3단계에서 만든 테이블에 데이터를 삽입합니다.
            table_name = ""
            profile_data = {}
            
            if user_data.role == 'mentor':
                table_name = 'mentor_profiles'
                profile_data = {
                    "id": str(new_user_id), # auth.users의 id와 동일하게 설정
                    "full_name": user_data.full_name
                    # "career_info": user_data.career_info 
                    # (AI 임베딩은 별도 API에서 처리하는 것을 권장)
                }
            elif user_data.role == 'mentee':
                table_name = 'mentee_profiles'
                profile_data = {
                    "id": str(new_user_id),
                    "full_name": user_data.full_name
                    # "current_situation": user_data.current_situation
                }
            else:
                raise HTTPException(status_code=400, detail="Invalid role specified")
            
            # 4. 해당 프로필 테이블에 데이터 삽입
            profile_response = supabase.table(table_name).insert(profile_data).execute()
            
            if profile_response.data:
                print(f"Successfully created profile for {user_data.role}: {new_user_id}")
                return {"message": f"User {user_data.email} created as {user_data.role}", "user_id": new_user_id}
            else:
                # (롤백 로직이 필요할 수 있으나, MVP에서는 에러 리포트로 대체)
                raise HTTPException(status_code=500, detail="Failed to create user profile")

        elif response.user is None and response.session is None:
             raise HTTPException(status_code=400, detail="User already exists")
        else:
             raise HTTPException(status_code=500, detail=str(response.model_dump()))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))