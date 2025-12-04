# File: backend/main.py


from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.api import mentors
from fastapi.middleware.cors import CORSMiddleware
from app.core.api import auth
from app.core.api import matching
from app.core.api import location
from app.core.api import availability
from app.core.api import bookings
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from app.core.api import coffeechats
from app.core.api import profile
from app.core.api import ai_generation
from app.core.api import chat


# 🚨 ⭐️ 핵심: FastAPI 앱 인스턴스를 생성합니다. ⭐️
app = FastAPI()

app.include_router(ai_generation.router) # 라우터 등록
# JSON 응답 직렬화(Serialization) 로직 정의 및 연결
def json_datetime_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return jsonable_encoder(obj)

# 앱에 커스텀 인코더 연결 (최종 방어)
app.json_encoder = json_datetime_encoder

# 2. origins 목록
origins = [
    "http://localhost:5173", # 👈 '수민'님의 Vue.js 주소 (포트 확인!)
    "http://127.0.0.1:5173",
    # (만약 '수민'님 Vue.js가 5174 등 다른 포트라면 그것도 추가)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 👈 origins 목록의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],         # 👈 모든 HTTP 메소드 허용
    allow_headers=["*"],         # 👈 모든 HTTP 헤더 허용
)

# 라우터들을 앱에 포함 (라우터 파일은 모두 app.api 폴더에 있습니다)
app.include_router(mentors.router)
app.include_router(auth.router)
app.include_router(matching.router)
app.include_router(location.router)
app.include_router(availability.router)
app.include_router(bookings.router)
app.include_router(profile.router)
app.include_router(chat.router)
  
# (다른 라우터들도 포함)
# app.include_router(auth.router)
# ...
app.include_router(coffeechats.router) # 👈 coffeechats 라우터 포함

@app.get("/")
def read_root():
    return {"message": "CoffeeChat-Platform API"}

if __name__ == "__main__":
    import uvicorn
    # reload=True는 개발 시 매우 유용합니다.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)