# backend/main.py
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    ai_generation,
    auth,
    availability,
    bookings,
    chat,
    location,
    matching,
    mentors,
    profile,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="CoffeeChat API")

# 허용할 프론트 주소. 배포 시 CORS_ORIGINS="https://a.com,https://b.com" 로 지정
origins = os.environ.get(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (auth, mentors, matching, location, availability, bookings, profile, chat, ai_generation):
    app.include_router(module.router)


@app.get("/")
def read_root():
    return {"message": "CoffeeChat-Platform API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
