from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from ..auth_utils import create_access_token, get_current_user
import bcrypt
from typing import Optional, Dict
import uuid
import json
import time
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api/auth", tags=["auth"])


# Password hashing helpers (using bcrypt directly, avoiding passlib compat issues)
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# ── Persistent user store ───────────────────────────────────────────
USERS_FILE = Path(__file__).parent.parent.parent / "users.json"
_users: Dict[str, dict] = {}
_initialized = False


def _save_users():
    """Persist users dict to disk so data survives restarts."""
    # Strip hashed_password from serialization? No, we need it. Save everything.
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(_users, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Silently fail if disk write fails


def _load_users():
    """Load users from the JSON file on disk."""
    global _users
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                _users = json.load(f)
        except (json.JSONDecodeError, Exception):
            _users = {}


def _init_default_users():
    global _initialized
    if _initialized:
        return
    # Try to load from disk first
    _load_users()
    # Only create defaults if they don't already exist
    if "admin" not in _users:
        _users["admin"] = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@expertlink.io",
            "full_name": "Admin User",
            "headline": "Platform Administrator",
            "hashed_password": hash_password("admin"),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "role": "admin",
        }
    if "demo" not in _users:
        _users["demo"] = {
            "id": str(uuid.uuid4()),
            "username": "demo",
            "email": "demo@expertlink.io",
            "full_name": "Demo User",
            "headline": "Software Engineer at ExpertLink",
            "hashed_password": hash_password("demo123"),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "role": "user",
        }
    _save_users()
    _initialized = True


def get_user_by_username(username: str) -> Optional[dict]:
    """Look up a user by username. Initializes users on first call."""
    _init_default_users()
    return _users.get(username.lower())


# ── Rate limiting for login ────────────────────────────────────────
_login_attempts: Dict[str, list] = {}  # username -> [timestamps]
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 300  # 5-minute window


def _check_rate_limit(username: str):
    """Raise 429 if the user has exceeded login attempt limits."""
    now = time.time()
    attempts = _login_attempts.get(username, [])
    # Prune old attempts outside the window
    attempts = [t for t in attempts if now - t < LOGIN_WINDOW_SECONDS]
    _login_attempts[username] = attempts
    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {LOGIN_WINDOW_SECONDS // 60} minutes.",
        )


def _record_attempt(username: str):
    """Record a failed login attempt."""
    _login_attempts.setdefault(username, []).append(time.time())


# ── RBAC Dependency ─────────────────────────────────────────────────
VALID_ROLES = ["admin", "manager", "user"]


def require_role(*allowed_roles: str):
    """FastAPI dependency that enforces role-based access."""
    async def _check(current_username: str = Depends(get_current_user)):
        _init_default_users()
        user = _users.get(current_username.lower())
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_role = user.get("role", "user")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}",
            )
        return current_username
    return _check


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
    role: str


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    headline: str
    created_at: str
    role: str


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
        "hashed_password": hash_password(req.password),
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
        "role": "user",
    }
    # Persist to disk
    _save_users()

    return {
        "id": user_id,
        "username": req.username,
        "email": req.email,
        "full_name": req.full_name,
        "message": "Registration successful! You can now sign in.",
    }


# ── Login (with rate limiting) ─────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    _init_default_users()

    username_key = form_data.username.lower()

    # Rate-limit check BEFORE password verification
    _check_rate_limit(username_key)

    user = _users.get(username_key)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        _record_attempt(username_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Successful login clears attempt history
    _login_attempts.pop(username_key, None)

    access_token = create_access_token(data={"sub": user["username"], "role": user.get("role", "user")})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": user.get("role", "user"),
    }


# ── Get Current User Profile (uses actual JWT) ────────────────────
@router.get("/me", response_model=UserProfile)
async def get_me(current_username: str = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    _init_default_users()

    user = _users.get(current_username.lower())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "headline": user["headline"],
        "created_at": user["created_at"],
        "role": user.get("role", "user"),
    }


# ── Admin-only: Manage Users ───────────────────────────────────────
@router.get("/users")
async def list_users(admin: str = Depends(require_role("admin"))):
    """List all users (admin only)."""
    return [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "full_name": u["full_name"],
            "role": u.get("role", "user"),
            "is_active": u.get("is_active", True),
            "created_at": u.get("created_at", ""),
        }
        for u in _users.values()
    ]


@router.put("/users/{username}/role")
async def update_user_role(
    username: str,
    role: str,
    admin: str = Depends(require_role("admin")),
):
    """Update a user's role (admin only). Valid roles: admin, manager, user."""
    _init_default_users()
    if role not in VALID_ROLES:
        raise HTTPException(400, detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}")
    user = _users.get(username.lower())
    if not user:
        raise HTTPException(404, detail="User not found")
    user["role"] = role
    _save_users()
    return {"message": f"Role for {username} updated to {role}", "username": username, "role": role}
