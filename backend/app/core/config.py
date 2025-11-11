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

# 👈 4. ⭐️ URL이 제대로 로드됐는지 터미널에 출력 (디버깅용) ⭐️
print(f"---- CONFIG: .env에서 로드한 URL: {SUPABASE_URL} ----")

# Supabase 클라이언트 인스턴스 생성
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("---- CONFIG ERROR: .env 파일 로드 실패! URL 또는 KEY가 없습니다. ----")
    # 개발 환경에서는 None으로 클라이언트를 생성하면 어차피 쿼리가 실패합니다.
    supabase: Client = None 
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("Supabase client initialized (Backend)")