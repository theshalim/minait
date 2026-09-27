"""Minimalist client dashboard: active orders, receipts, order history."""
from fastapi import APIRouter, Depends, Request

from app.security import CurrentUser, require_user
from app.supabase_client import supabase_admin
from app.templating import base_ctx, templates

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(request: Request, user: CurrentUser = Depends(require_user)):
    orders = (
        supabase_admin()
        .table("orders")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
        .data
    )
    return templates.TemplateResponse("dashboard.html", base_ctx(request, orders=orders))
