# backend/app/core/config.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv # 이 줄을 추가합니다

load_dotenv() # .env 파일에서 환경 변수를 불러옵니다

# .env 파일에서 변수를 안전하게 불러옵니다
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

# Supabase 클라이언트 인스턴스 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("Supabase client initialized (Backend)")