# test_ai.py
import google.generativeai as genai
import sys

# API 키 설정 (여기에 본인 키를 넣어주세요)
GOOGLE_API_KEY = "AIzaSyDdqWpHXbocB7btkU0a1scdwmz_LxLz0iE" 
genai.configure(api_key=GOOGLE_API_KEY)

print("--- [진단 시작] ---")
print(f"🐍 실행 파이썬: {sys.executable}")
print(f"📦 라이브러리 버전: {genai.__version__}")

print("\n📋 사용 가능한 모델 목록:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
except Exception as e:
    print(f"❌ 모델 목록 조회 실패: {e}")

print("\n🚀 [gemini-1.5-flash] 테스트 시도:")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("안녕")
    print(f"✅ 성공! 응답: {response.text}")
except Exception as e:
    print(f"🔥 실패: {e}")

print("--- [진단 끝] ---")