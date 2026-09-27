"""Signup / login / logout using Supabase Auth."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.security import (
    CurrentUser,
    clear_session_cookies,
    get_optional_user,
    set_session_cookies,
)
from app.supabase_client import supabase_admin, supabase_auth
from app.templating import base_ctx, templates

router = APIRouter(tags=["auth"])


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

    supabase_admin().table("profiles").upsert(
        {"id": result.user.id, "full_name": full_name, "phone": phone}
    ).execute()

    response = RedirectResponse("/dashboard", status_code=303)
    set_session_cookies(response, result.session.access_token, result.session.refresh_token)
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
