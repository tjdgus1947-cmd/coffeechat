from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, mentors, mentees, matching, network

app = FastAPI(
    title="CoffeeChat Platform API",
    version="1.0.0",
    description="AI-powered mentor-mentee matching platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(mentors.router, prefix="/api/mentors", tags=["mentors"])
app.include_router(mentees.router, prefix="/api/mentees", tags=["mentees"])
app.include_router(matching.router, prefix="/api/matching", tags=["matching"])
app.include_router(network.router, prefix="/api/network", tags=["network"])

@app.get("/")
def read_root():
    return {
        "message": "CoffeeChat Platform API",
        "version": "1.0.0",
        "demo_mode": settings.DEMO_MODE
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)