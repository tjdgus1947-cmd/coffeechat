# backend/app/core/config.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path  # 👈 1. pathlib 임포트

# 👈 2. .env 파일의 절대 경로를 계산합니다.
# 현재 파일(config.py) -> app/core -> app -> backend 폴더
# 즉, backend 폴더에 있는 .env 파일을 가리킵니다.
env_path = Path(__file__).parent.parent.parent / '.env'

# 👈 3. .env 파일 경로를 명시적으로 지정해서 로드
load_dotenv(dotenv_path=env_path)

# .env 파일에서 변수를 안전하게 불러옵니다
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")


# Supabase 클라이언트 인스턴스 생성
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("---- CONFIG ERROR: .env 파일 로드 실패! URL 또는 KEY가 없습니다. ----")
    # 개발 환경에서는 None으로 클라이언트를 생성하면 어차피 쿼리가 실패합니다.
    supabase: Client = None 
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("Supabase client initialized (Backend)")

def new_auth_client() -> Client:
    """
    회원가입·로그인 전용 일회용 클라이언트.

    supabase-py 클라이언트는 sign_up / sign_in 이 성공하면 그 사용자의 토큰으로
    Authorization 헤더를 바꾼다. 공용 `supabase`(service_role)로 로그인하면 이후 모든 DB 요청이
    "마지막으로 로그인한 사용자" 권한으로 나가서 RLS 에 막히거나, 남의 권한으로 실행된다.
    그래서 인증 작업은 요청마다 새 클라이언트에서 하고, 세션은 저장하지 않는다.
    """
    from supabase import ClientOptions

    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_KEY,
        options=ClientOptions(persist_session=False, auto_refresh_token=False),
    )
