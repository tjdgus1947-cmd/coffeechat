# backend/main.py

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api import mentors # 8.1에서 만든 mentors.py 임포트
# (wbs_detail.md의 다른 라우터들도 임포트)
# from app.api import auth, mentees, matching, network 
from app.api import auth # 9단계에서 방금 추가함
from app.api import matching
from app.api import location
from app.api import availability

app = FastAPI()

# 2. origins 목록에 Vue.js 서버 주소를 추가합니다.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5176",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 👈 origins 목록의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],         # 👈 모든 HTTP 메소드 허용
    allow_headers=["*"],         # 👈 모든 HTTP 헤더 허용
)

# 멘토 API 라우터를 앱에 포함
app.include_router(mentors.router) 
app.include_router(auth.router)
app.include_router(matching.router)
app.include_router(location.router)
app.include_router(availability.router)

# (다른 라우터들도 포함)
# app.include_router(auth.router)
# ...

@app.get("/")
def read_root():
    return {"message": "CoffeeChat-Platform API"}

# (wbs_detail.md의 uvicorn 실행 부분)
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    # VS Code에서 디버깅 시에는 아래 줄이 더 편리할 수 있습니다.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)