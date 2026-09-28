"""Admin login / logout using Supabase Auth.

There is exactly one admin and no customer accounts (customers order on
WhatsApp), so there is no public sign-up and no login link on the site: the
admin opens /login (or /admin) by URL. The admin changes their password in
Admin -> Account; a forgotten password is reset from the Supabase dashboard
(Authentication -> Users), since the site sends no email.
"""
import logging

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.i18n import get_locale, make_translator
from app.security import (
    CurrentUser,
    clear_session_cookies,
    get_optional_user,
    set_session_cookies,
)
from app.supabase_client import supabase_admin, supabase_auth
from app.templating import base_ctx, templates

router = APIRouter(tags=["auth"])
logger = logging.getLogger("minait")


@router.get("/signup")
def signup_closed():
    return RedirectResponse("/login", status_code=303)


@router.get("/dashboard")
def old_dashboard():
    # Customer dashboards are gone; the only account is the admin's.
    return RedirectResponse("/admin", status_code=303)


@router.post("/auth/session")
def create_session_from_tokens(payload: dict = Body(...)):
    """Called by static/js/main.js after Supabase redirects back here with
    `#access_token=...&refresh_token=...` in the URL fragment (e.g. a
    password-reset link sent from the Supabase dashboard). The fragment never
    reaches the server on its own, so the client-side script forwards it
    here, we validate it against Supabase, and turn it into our normal
    session cookies."""
    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Missing tokens")

    try:
        result = supabase_auth().auth.get_user(access_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    if not result.user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    try:
        supabase_admin().table("profiles").upsert({"id": result.user.id}, on_conflict="id").execute()
    except Exception:
        logger.exception("Failed to upsert profile for user %s", result.user.id)

    response = JSONResponse({"ok": True})
    set_session_cookies(response, access_token, refresh_token)
    return response


@router.get("/login")
def login_page(request: Request, user: CurrentUser | None = Depends(get_optional_user)):
    if user and user.is_admin:
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("login.html", base_ctx(request, error=None))


@router.post("/login")
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        result = supabase_auth().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception:
        return templates.TemplateResponse(
            "login.html",
            base_ctx(request, error=make_translator(get_locale(request))("login.invalid")),
            status_code=401,
        )

    response = RedirectResponse("/admin", status_code=303)
    set_session_cookies(response, result.session.access_token, result.session.refresh_token)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    clear_session_cookies(response)
    return response
