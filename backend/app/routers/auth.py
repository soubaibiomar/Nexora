from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from ..auth_utils import create_access_token
from passlib.context import CryptContext
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── In-memory user store ────────────────────────────────────────────
_users: dict = {}
_initialized = False


def _init_default_users():
    global _initialized
    if _initialized:
        return
    # Default admin user
    _users["admin"] = {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "email": "admin@expertlink.io",
        "full_name": "Admin User",
        "headline": "Platform Administrator",
        "hashed_password": pwd_context.hash("admin"),
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
    }
    # Demo user
    _users["demo"] = {
        "id": str(uuid.uuid4()),
        "username": "demo",
        "email": "demo@expertlink.io",
        "full_name": "Demo User",
        "headline": "Software Engineer at ExpertLink",
        "hashed_password": pwd_context.hash("demo123"),
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
    }
    _initialized = True


# ── Models ──────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str
    password: str = Field(..., min_length=4)
    full_name: str = Field(..., min_length=2)
    headline: Optional[str] = ""


class RegisterResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    message: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    full_name: str
    email: str


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    headline: str
    created_at: str


# ── Register ────────────────────────────────────────────────────────
@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(req: RegisterRequest):
    _init_default_users()

    # Check if username already exists
    if req.username.lower() in _users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Check if email already exists
    for user in _users.values():
        if user["email"].lower() == req.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Create user
    user_id = str(uuid.uuid4())
    _users[req.username.lower()] = {
        "id": user_id,
        "username": req.username,
        "email": req.email,
        "full_name": req.full_name,
        "headline": req.headline or "",
        "hashed_password": pwd_context.hash(req.password),
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
    }

    return {
        "id": user_id,
        "username": req.username,
        "email": req.email,
        "full_name": req.full_name,
        "message": "Registration successful! You can now sign in.",
    }


# ── Login ───────────────────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    _init_default_users()

    user = _users.get(form_data.username.lower())
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
    }


# ── Get Current User Profile ───────────────────────────────────────
@router.get("/me", response_model=UserProfile)
async def get_me():
    _init_default_users()
    # For demo: return the first user. In production, use token-based auth.
    token_user = "admin"
    user = _users.get(token_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "headline": user["headline"],
        "created_at": user["created_at"],
    }
