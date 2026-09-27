"""Auth helpers built on top of Supabase Auth.

Session is kept in two httponly cookies (`sb_access_token`, `sb_refresh_token`)
set on login/signup. Every request that needs to know "who is logged in"
validates the access token against Supabase directly — no JWT secret handling
needed on our side.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from app.supabase_client import supabase_admin, supabase_auth

ACCESS_COOKIE = "sb_access_token"
REFRESH_COOKIE = "sb_refresh_token"


@dataclass
class CurrentUser:
    id: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_admin: bool = False


def set_session_cookies(response, access_token: str, refresh_token: str) -> None:
    common = dict(httponly=True, samesite="lax", secure=True, path="/")
    response.set_cookie(ACCESS_COOKIE, access_token, max_age=60 * 60 * 24 * 7, **common)
    response.set_cookie(REFRESH_COOKIE, refresh_token, max_age=60 * 60 * 24 * 30, **common)


def clear_session_cookies(response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")


def _load_profile(user_id: str) -> dict:
    res = (
        supabase_admin()
        .table("profiles")
        .select("full_name, phone, is_admin")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    return res.data or {}


def get_optional_user(request: Request) -> Optional[CurrentUser]:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        return None
    try:
        result = supabase_auth().auth.get_user(token)
    except Exception:
        return None
    user = getattr(result, "user", None)
    if not user:
        return None
    profile = _load_profile(user.id)
    return CurrentUser(
        id=user.id,
        email=user.email or "",
        full_name=profile.get("full_name"),
        phone=profile.get("phone"),
        is_admin=bool(profile.get("is_admin")),
    )


def require_user(user: Optional[CurrentUser] = Depends(get_optional_user)) -> CurrentUser:
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


def require_admin(user: CurrentUser = Depends(require_user)) -> CurrentUser:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access only")
    return user
