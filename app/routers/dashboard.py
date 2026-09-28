"""Minimalist client dashboard: active orders, receipts, order history, and
changing your own password."""
import logging

from fastapi import APIRouter, Depends, Form, Request

from app.i18n import get_locale, make_translator
from app.security import CurrentUser, check_password, require_user
from app.supabase_client import supabase_admin
from app.templating import base_ctx, templates

router = APIRouter(tags=["dashboard"])
logger = logging.getLogger("minait")


def _render(request: Request, user: CurrentUser, **extra):
    orders = (
        supabase_admin()
        .table("orders")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
        .data
    )
    return templates.TemplateResponse("dashboard.html", base_ctx(request, orders=orders, **extra))


@router.get("/dashboard")
def dashboard(request: Request, user: CurrentUser = Depends(require_user)):
    return _render(request, user)


@router.post("/dashboard/password")
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    user: CurrentUser = Depends(require_user),
):
    t = make_translator(get_locale(request))
    if len(new_password) < 6:
        return _render(request, user, password_error=t("dashboard.password_short"))
    try:
        if not check_password(user.email, current_password):
            return _render(request, user, password_error=t("dashboard.password_wrong"))
        supabase_admin().auth.admin.update_user_by_id(user.id, {"password": new_password})
    except Exception:
        logger.exception("Password change failed for user %s", user.id)
        return _render(request, user, password_error=t("dashboard.password_failed"))
    return _render(request, user, password_message=t("dashboard.password_changed"))
