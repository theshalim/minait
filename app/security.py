"""Auth helpers built on top of Supabase Auth.

Session is kept in two httponly cookies (`sb_access_token`, `sb_refresh_token`)
set on login/signup. Every request that needs to know "who is logged in"
validates the access token against Supabase directly — no JWT secret handling
needed on our side.

Supabase access tokens only live ~1 hour, so `refresh_session_middleware`
(wired up in main.py) swaps an expired/expiring access token for a fresh one
using the refresh token, before the request reaches any route. Without it,
everyone would be silently logged out an hour after logging in.
"""
from __future__ import annotations

import base64
import json
import logging
import time
from dataclasses import dataclass
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.supabase_client import supabase_admin, supabase_auth

ACCESS_COOKIE = "sb_access_token"
REFRESH_COOKIE = "sb_refresh_token"
# Refresh a little before the real expiry, so a token can't expire mid-request.
REFRESH_MARGIN_SECONDS = 120

logger = logging.getLogger("minait")


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


# ---------------------------------------------------------------------------
# Direct calls to Supabase's auth REST API. Used instead of the SDK's
# session-based helpers because the SDK client is shared by every visitor —
# storing one visitor's session on it (and letting it auto-refresh in the
# background) would be wrong for everyone else.
# ---------------------------------------------------------------------------
def _auth_token_request(grant_type: str, body: dict) -> Optional[dict]:
    """POST /auth/v1/token. Returns the token JSON on success, None when
    Supabase rejects the credentials. Network errors are raised."""
    resp = httpx.post(
        f"{settings.SUPABASE_URL}/auth/v1/token",
        params={"grant_type": grant_type},
        headers={"apikey": settings.SUPABASE_ANON_KEY},
        json=body,
        timeout=10,
    )
    if resp.status_code >= 400:
        return None
    return resp.json()


def refresh_tokens(refresh_token: str) -> Optional[dict]:
    return _auth_token_request("refresh_token", {"refresh_token": refresh_token})


def check_password(email: str, password: str) -> bool:
    return _auth_token_request("password", {"email": email, "password": password}) is not None


def _jwt_exp(token: str) -> Optional[int]:
    """Reads the `exp` claim without verifying the signature — only used to
    decide *when* to refresh; Supabase still validates the token itself."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return int(json.loads(base64.urlsafe_b64decode(payload))["exp"])
    except Exception:
        return None


def _needs_refresh(access_token: Optional[str]) -> bool:
    if not access_token:
        return True
    exp = _jwt_exp(access_token)
    return exp is None or exp - time.time() < REFRESH_MARGIN_SECONDS


def _replace_cookies(request: Request, updates: dict) -> None:
    """Rewrites the request's Cookie header so everything downstream (routes,
    dependencies, templates) sees the refreshed tokens. A value of None
    removes that cookie."""
    cookies = dict(request.cookies)
    for name, value in updates.items():
        if value is None:
            cookies.pop(name, None)
        else:
            cookies[name] = value
    header = "; ".join(f"{k}={v}" for k, v in cookies.items()).encode("latin-1")
    headers = [(k, v) for k, v in request.scope["headers"] if k != b"cookie"]
    if header:
        headers.append((b"cookie", header))
    request.scope["headers"] = headers


async def refresh_session_middleware(request: Request, call_next):
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if (
        not refresh_token
        or request.url.path.startswith("/static")
        or not _needs_refresh(request.cookies.get(ACCESS_COOKIE))
    ):
        return await call_next(request)

    try:
        tokens = await run_in_threadpool(refresh_tokens, refresh_token)
    except Exception:
        # Supabase unreachable: don't log anyone out over a network blip.
        logger.exception("Session refresh failed (network)")
        return await call_next(request)

    if not tokens:
        # Refresh token expired or revoked — the session is really over.
        _replace_cookies(request, {ACCESS_COOKIE: None, REFRESH_COOKIE: None})
        response = await call_next(request)
        clear_session_cookies(response)
        return response

    _replace_cookies(
        request,
        {ACCESS_COOKIE: tokens["access_token"], REFRESH_COOKIE: tokens["refresh_token"]},
    )
    response = await call_next(request)
    # Don't overwrite cookies a route just set itself (login, logout).
    if not any(k == b"set-cookie" and ACCESS_COOKIE.encode() in v for k, v in response.raw_headers):
        set_session_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return response


def _load_profile(user_id: str) -> dict:
    try:
        res = (
            supabase_admin()
            .table("profiles")
            .select("full_name, phone, is_admin")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        return (res.data if res else None) or {}
    except Exception:
        # A hiccup here (network blip, row missing, etc.) should never take
        # a public page down — worst case we just don't know the profile
        # details yet and fall back to the defaults below.
        return {}


def _lookup_user(request: Request) -> Optional[CurrentUser]:
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


def get_optional_user(request: Request) -> Optional[CurrentUser]:
    # Cached per request: routes, their dependencies and base_ctx() all ask,
    # and each lookup is two network calls to Supabase.
    if "minait_user" not in request.scope:
        request.scope["minait_user"] = _lookup_user(request)
    return request.scope["minait_user"]


def require_user(user: Optional[CurrentUser] = Depends(get_optional_user)) -> CurrentUser:
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


def require_admin(user: CurrentUser = Depends(require_user)) -> CurrentUser:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access only")
    return user
