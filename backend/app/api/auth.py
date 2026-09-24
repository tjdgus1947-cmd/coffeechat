from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import supabase, new_auth_client
from app.services.ml_service import generate_embedding
import uuid
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
# supabase-py 2.8+ 에서 인증 패키지 이름이 gotrue → supabase_auth 로 바뀌었다. 둘 다 지원한다.
try:
    from supabase_auth.errors import AuthApiError
    from supabase_auth.types import User
except ImportError:  # 구버전 supabase-py
    from gotrue.errors import AuthApiError
    from gotrue.types import User


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
   
    try:
        
    
        response = supabase.auth.get_user(token)
        user = response.user

        if not user:
            print("❌ 토큰 검증 실패: user 객체가 None")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return user

    except AuthApiError as e:
        print(f"❌ Supabase Auth 오류: {e.message}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {e.message}")

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")


def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
 
    if not current_user:
        print("❌ current_user가 None입니다.")
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = str(current_user.id)
    return user_id



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
def sign_up_mentor(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...), 
    company: str = Form(...),   
    team: str = Form(...),
    experienceYears: int = Form(0),
    topics: str = Form(...),
    # ⭐️ AI 생성 자기소개를 받을 필드
    introduction: Optional[str] = Form(None), 
    # 🆕 위치 정보
    latitude: float = Form(37.5665),
    longitude: float = Form(126.9780),
    # ⭐️ 증빙 서류 파일 (선택)
    proofFile: Optional[UploadFile] = File(None)
):
    """
    멘토 회원가입 (FormData 방식 + 파일 업로드)
    """
    try:
        # 1. Supabase Auth에 사용자 생성
        response = new_auth_client().auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "role": "mentor", 
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
            "role": "mentor"
        }).execute()
        
        if not user_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create user profile in public.users")
        
        # 3. 상세 프로필 데이터 준비
        # introduction(AI본)이 있으면 쓰고, 없으면 자동 조합
        intro_text = introduction if introduction else f"안녕하세요, {experienceYears}년차 {topics} 전문가입니다."
        
        career_info_text = f"회사: {company}, 직무: {team}, 경력: {experienceYears}년, 전문분야: {topics}, 소개: {intro_text}"
        location_point = f"POINT({longitude} {latitude})"
        
        # 4. AI 임베딩 생성
        embedding_vector = None
        try:
            # 검색이 잘 되도록 주요 키워드 포함하여 임베딩
            text_to_embed = f"전문분야: {topics}. 경력: {experienceYears}년. 회사: {company}. 소개: {intro_text}"
            embedding_vector = generate_embedding(text_to_embed)
        except Exception as e:
            print(f"⚠️ Embedding generation failed: {e}")
        
        # 5. 파일 처리 (여기서는 실제 저장은 생략하고 로그만 출력합니다)
        # 실제로는 Supabase Storage에 업로드하고 URL을 받아와야 합니다.
        proof_file_url = None
        if proofFile:
            print(f"📂 증빙 서류 수신: {proofFile.filename}")
            # 추후 구현: supabase.storage.from('proofs').upload(...)
            # proof_file_url = "uploaded_url_here"

        # 6. mentor_profiles 테이블에 상세 프로필 생성
        # ⭐️ verification_status를 'pending'(승인 대기)으로 설정
        mentor_profile_response = supabase.table('mentor_profiles').insert({
            "user_id": str(new_user_id), 
            "career_info": career_info_text,
            "location": location_point,
            "embedding": embedding_vector,
            "verification_status": "pending" # 관리자 승인 대기
        }).execute()
            
        if not mentor_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentor_profiles entry")
        
        print(f"✅ Mentor {new_user_id} registered. (Status: Pending)")
                
        return {
            "user": response.user,
            "message": "멘토 가입 신청 완료. 관리자 승인 후 활동 가능합니다.",
            "location": {"latitude": latitude, "longitude": longitude}
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 멘토 가입 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 멘티 회원가입 (FormData 방식) ---
@router.post("/api/auth/register/mentee")
def sign_up_mentee(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...), 
    situation: Optional[str] = Form(None), 
    topics: Optional[str] = Form(None),
    # ⭐️ 추가: AI가 생성한 자기소개를 받는 필드
    introduction: Optional[str] = Form(None), 
    # 🆕 위치 정보 추가 (기본값 설정으로 422 에러 방지)
    latitude: float = Form(37.5665), # 서울 시청 좌표 기본값
    longitude: float = Form(126.9780),
    proofFile: Optional[UploadFile] = File(None) 
):
    """
    멘티 회원가입 (FormData 방식)
    """
    try:
        # ... (이하 로직은 기존과 동일하게 유지) ...
        
        # 1. Supabase Auth에 사용자 생성
        response = new_auth_client().auth.sign_up({
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

        # 3. mentee_profiles 테이블 데이터 준비
        final_situation_text = introduction if introduction else situation
        text_to_embed = f"현재 상황: {situation}. 희망 진로: {topics}. 자기소개: {final_situation_text}"
        location_point = f"POINT({longitude} {latitude})"
        
        embedding_vector = None
        try:
            embedding_vector = generate_embedding(text_to_embed)
        except Exception as e:
            print(f"⚠️ Embedding generation failed: {e}")
            
        mentee_profile_response = supabase.table('mentee_profiles').insert({
            "user_id": str(new_user_id), 
            "current_situation": final_situation_text, 
            "career_goal": topics,
            "location": location_point,
            "embedding": embedding_vector
        }).execute()
        
        print(f"✅ Mentee {new_user_id} registered with embedding and location.")

        if not mentee_profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create mentee_profiles entry")
       
        return {
            "user": response.user,
            "message": "멘티 회원가입 완료.",
            "location": {"latitude": latitude, "longitude": longitude}
        }

    except HTTPException:
        raise
    except Exception as e:
        # 에러 로그를 더 자세히 출력
        print(f"🔥 멘티 가입 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 로그인 (공통) ---
@router.post("/api/auth/login")
def sign_in(user_data: UserSignIn):
    try:
        response = new_auth_client().auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        print(f"✅ 로그인 성공: {response.user.id if response.user else 'No user'}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 로그인 실패: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")