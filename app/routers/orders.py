"""Ordering and order status pages.

Customers order through the website form (routers/enquiry.py), or by
calling / chatting, and the admin logs those in Admin -> Orders. Each order's
unique, hard-to-guess
order_number is the lookup key for the public order status page (the
tracking link sent to the customer), like a receipt link.

The Stripe/SSLCOMMERZ code (payments.py, webhooks.py, the thank-you page
below) is kept dormant for if online payment is ever switched back on.
"""
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.notify import notify_payment_received
from app.payments import retrieve_stripe_session
from app.supabase_client import fetch_one, supabase_admin
from app.templating import base_ctx, templates

router = APIRouter(tags=["orders"])
logger = logging.getLogger("minait")


@router.get("/checkout/{slug}")
def checkout(slug: str):
    """Old checkout links now open the order form for that service."""
    return RedirectResponse(f"/order/service/{slug}", status_code=303)


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
