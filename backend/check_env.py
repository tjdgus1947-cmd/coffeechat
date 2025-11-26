# check_env.py
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("SUPABASE_SERVICE_KEY")
url = os.getenv("SUPABASE_URL")

print("---------- [환경변수 정밀 검사] ----------")
print(f"URL 길이: {len(url) if url else 0}")
print(f"URL 내용: {repr(url)}")  # repr()을 쓰면 숨겨진 문자까지 다 보입니다.
print("-" * 30)
print(f"KEY 길이: {len(key) if key else 0}")
print(f"KEY 내용: {repr(key)}")
print("------------------------------------------")

# 한글 포함 여부 체크
try:
    if key:
        key.encode('ascii')
        print("✅ KEY: 정상 (ASCII)")
    else:
        print("❌ KEY: 비어있음")
except UnicodeEncodeError as e:
    print(f"❌ KEY: 에러 발생! 범인 발견! -> {e}")