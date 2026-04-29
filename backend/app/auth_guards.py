"""
Centralized RBAC Guards for Nexora.

Usage in any router:
    from ..auth_guards import require_auth, require_manager, require_admin

    @router.get("/data")
    async def get_data(user: dict = Depends(require_auth)):
        ...

    @router.post("/admin-action")
    async def admin_action(user: dict = Depends(require_admin)):
        ...

Each guard returns the full user dict (id, username, role, etc.).
"""

from fastapi import Depends, HTTPException, status
from .auth_utils import get_current_user

# Lazy import to avoid circular dependency — the user store lives in auth.py
_users_ref = None


def _get_users_store() -> dict:
    """Lazily import the users store from the auth router."""
    global _users_ref
    if _users_ref is None:
        from .routers.auth import _users, _init_default_users
        _init_default_users()
        _users_ref = _users
    return _users_ref


def _resolve_user(username: str) -> dict:
    """Look up a user by username. Raises 401 if not found."""
    users = _get_users_store()
    user = users.get(username.lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
        )
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return user


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

async def require_auth(current_username: str = Depends(get_current_user)) -> dict:
    """Any authenticated user (user, manager, or admin)."""
    return _resolve_user(current_username)


async def require_manager(current_username: str = Depends(get_current_user)) -> dict:
    """Manager or admin only."""
    user = _resolve_user(current_username)
    if user.get("role", "user") not in ("manager", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required",
        )
    return user


async def require_admin(current_username: str = Depends(get_current_user)) -> dict:
    """Admin only."""
    user = _resolve_user(current_username)
    if user.get("role", "user") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
