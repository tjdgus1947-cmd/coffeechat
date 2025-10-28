from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    user_type: str  # "mentor" or "mentee"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    # Demo mode - always success
    return {
        "access_token": "demo-token-" + request.email,
        "token_type": "bearer",
        "user": {
            "id": "user-1",
            "email": request.email,
            "name": request.name,
            "user_type": request.user_type,
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    # Demo mode - always success
    if request.email == "mentee@example.com":
        return {
            "access_token": "demo-token-mentee",
            "token_type": "bearer",
            "user": {
                "id": "mentee-1",
                "email": request.email,
                "name": "김멘티",
                "user_type": "mentee",
            }
        }
    elif request.email == "mentor@example.com":
        return {
            "access_token": "demo-token-mentor",
            "token_type": "bearer",
            "user": {
                "id": "mentor-1",
                "email": request.email,
                "name": "이회계",
                "user_type": "mentor",
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/me")
async def get_current_user():
    """Get current user info"""
    # Demo mode - return demo mentee
    return {
        "id": "mentee-1",
        "email": "mentee@example.com",
        "name": "김멘티",
        "user_type": "mentee",
    }