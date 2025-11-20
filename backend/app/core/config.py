# backend/app/core/config.py


import os
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
import traceback

try:
    # .env 파일의 절대 경로 계산 및 로드
    env_path = Path(__file__).parent.parent.parent / '.env'
    print(f"[config.py] .env 경로: {env_path}")
    load_dotenv(dotenv_path=env_path)

    # 환경 변수 확인
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    print(f"[config.py] SUPABASE_URL: {SUPABASE_URL}")
    print(f"[config.py] SUPABASE_SERVICE_KEY: {SUPABASE_SERVICE_KEY[:8]}... (key 일부만 표시)")

    # Supabase 클라이언트 인스턴스 생성
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("[config.py] ---- CONFIG ERROR: .env 파일 로드 실패! URL 또는 KEY가 없습니다. ----")
        supabase: Client = None
    else:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("[config.py] Supabase client initialized (Backend)")
except Exception as e:
    print("[config.py] [오류 발생]")
    traceback.print_exc()