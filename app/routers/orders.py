"""Checkout, order creation and order status pages.

Guest checkout is allowed (no login required) — matching the "extremely
simple" UX goal. If the visitor is logged in, their profile pre-fills the
form. Every order gets a unique, hard-to-guess order_number that also acts as
the lookup key for the (public) order status page, like a receipt link.
"""
import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.notify import notify_new_order, notify_payment_received
from app.payments import (
    create_sslcommerz_session,
    create_stripe_checkout_session,
    retrieve_stripe_session,
)
from app.security import CurrentUser, get_optional_user
from app.supabase_client import fetch_one, supabase_admin
from app.templating import base_ctx, templates
from app.utils import generate_order_number, whatsapp_link

router = APIRouter(tags=["orders"])
logger = logging.getLogger("minait")


@router.get("/checkout/{slug}")
def checkout_page(request: Request, slug: str, user: CurrentUser | None = Depends(get_optional_user)):
    service = fetch_one(
        supabase_admin().table("services").select("*").eq("slug", slug).eq("is_active", True)
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return templates.TemplateResponse(
        "checkout.html",
        base_ctx(request, service=service, payment_methods=settings.payment_methods()),
    )


@router.post("/orders")
def create_order(
    request: Request,
    service_id: int = Form(...),
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    customer_phone: str = Form(""),
    notes: str = Form(""),
    payment_method: str = Form(...),  # 'stripe' | 'sslcommerz' | 'whatsapp'
    user: CurrentUser | None = Depends(get_optional_user),
):
    svc = fetch_one(supabase_admin().table("services").select("*").eq("id", service_id))
    if not svc or not svc["is_active"]:
        raise HTTPException(status_code=404, detail="Service not found")
    if payment_method not in settings.payment_methods():
        payment_method = "whatsapp"

    order = {
        "order_number": generate_order_number(),
        "user_id": user.id if user else None,
        "service_id": svc["id"],
        "service_title": svc["title"],
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "notes": notes,
        "amount": svc["price"],
        "currency": svc["currency"],
        "payment_method": payment_method,
        "payment_status": "unpaid",
        "status": "pending",
    }
    created = supabase_admin().table("orders").insert(order).execute().data[0]
    notify_new_order(created)

    if payment_method == "stripe":
        try:
            url = create_stripe_checkout_session(created)
            return RedirectResponse(url, status_code=303)
        except Exception:
            logger.exception("Stripe checkout session failed for order %s", created["order_number"])
            return RedirectResponse(
                f"/orders/{created['order_number']}?gateway_error=1", status_code=303
            )

    if payment_method == "sslcommerz":
        try:
            url = create_sslcommerz_session(created)
            return RedirectResponse(url, status_code=303)
        except Exception:
            logger.exception("SSLCOMMERZ session failed for order %s", created["order_number"])
            return RedirectResponse(
                f"/orders/{created['order_number']}?gateway_error=1", status_code=303
            )

    if payment_method == "whatsapp" and settings.WHATSAPP_NUMBER:
        text = (
            f"Hi {settings.SITE_NAME}! I just placed order {created['order_number']} "
            f"for '{svc['title']}' ({svc['price']} {svc['currency']}). "
            f"Name: {customer_name}."
        )
        return RedirectResponse(whatsapp_link(settings.WHATSAPP_NUMBER, text), status_code=303)

    return RedirectResponse(f"/orders/{created['order_number']}", status_code=303)


@router.get("/orders/{order_number}")
def order_status(request: Request, order_number: str, gateway_error: bool = False):
    order = fetch_one(supabase_admin().table("orders").select("*").eq("order_number", order_number))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return templates.TemplateResponse(
        "order_status.html", base_ctx(request, order=order, gateway_error=gateway_error)
    )


@router.get("/orders/{order_number}/thank-you")
def order_thank_you(request: Request, order_number: str, session_id: str | None = None):
    order = fetch_one(supabase_admin().table("orders").select("*").eq("order_number", order_number))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Defensive confirmation in case the Stripe webhook hasn't landed yet.
    if session_id and order["payment_status"] != "paid":
        try:
            session = retrieve_stripe_session(session_id)
            if session.payment_status == "paid":
                order = (
                    supabase_admin()
                    .table("orders")
                    .update({"payment_status": "paid", "payment_ref": session_id})
                    .eq("order_number", order_number)
                    .execute()
                    .data[0]
                )
                notify_payment_received(order)
        except Exception:
            pass

    return templates.TemplateResponse("order_status.html", base_ctx(request, order=order, just_paid=True))
