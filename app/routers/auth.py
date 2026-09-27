"""Signup / login / logout using Supabase Auth."""
import logging

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

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
def signup_page(request: Request, user: CurrentUser | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("signup.html", base_ctx(request, error=None))


@router.post("/signup")
def signup_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    password: str = Form(...),
):
    try:
        result = supabase_auth().auth.sign_up({"email": email, "password": password})
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        return templates.TemplateResponse(
            "signup.html", base_ctx(request, error=str(exc)), status_code=400
        )

    if result.user:
        # Save the name/phone from the form now — if email confirmation is
        # required, sign_up() returns a user without a session, and this is
        # the only place we'll ever see this data. on_conflict="id" makes
        # this a true upsert (merge) instead of a plain insert, which is
        # what was 409-ing when the same email signed up more than once.
        # Never let a hiccup here take down the whole signup.
        try:
            supabase_admin().table("profiles").upsert(
                {"id": result.user.id, "full_name": full_name, "phone": phone},
                on_conflict="id",
            ).execute()
        except Exception:
            logger.exception("Failed to upsert profile for user %s", result.user.id)

    if not result.session or not result.user:
        # Email confirmation is required by the Supabase project settings.
        return templates.TemplateResponse(
            "signup.html",
            base_ctx(
                request,
                error=None,
                message="Account created! Please check your email to confirm, then log in.",
            ),
        )

    response = RedirectResponse("/dashboard", status_code=303)
    set_session_cookies(response, result.session.access_token, result.session.refresh_token)
    return response


@router.post("/auth/session")
def create_session_from_tokens(payload: dict = Body(...)):
    """Called by static/js/main.js after Supabase redirects back here with
    `#access_token=...&refresh_token=...` in the URL fragment (email
    confirmation and password-reset links both do this). The fragment never
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
        supabase_admin().table("profiles").upsert(
            {"id": result.user.id}, on_conflict="id"
        ).execute()
    except Exception:
        logger.exception("Failed to upsert profile for user %s", result.user.id)

    response = JSONResponse({"ok": True})
    set_session_cookies(response, access_token, refresh_token)
    return response


@router.get("/login")
def login_page(request: Request, user: CurrentUser | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=303)
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
            base_ctx(request, error="Invalid email or password."),
            status_code=401,
        )

    response = RedirectResponse("/dashboard", status_code=303)
    set_session_cookies(response, result.session.access_token, result.session.refresh_token)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    clear_session_cookies(response)
    return response
