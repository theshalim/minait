"""Server-to-server payment confirmations. These are the source of truth for
marking an order paid — never trust a browser redirect alone."""
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.notify import notify_payment_received
from app.payments import construct_stripe_webhook_event, validate_sslcommerz_payment
from app.supabase_client import supabase_admin

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _mark_paid(order_number: str, payment_ref: str) -> dict | None:
    existing = (
        supabase_admin()
        .table("orders")
        .select("*")
        .eq("order_number", order_number)
        .maybe_single()
        .execute()
        .data
    )
    if not existing or existing["payment_status"] == "paid":
        return existing
    updated = (
        supabase_admin()
        .table("orders")
        .update({"payment_status": "paid", "payment_ref": payment_ref})
        .eq("order_number", order_number)
        .execute()
        .data[0]
    )
    notify_payment_received(updated)
    return updated


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = construct_stripe_webhook_event(payload, sig_header)
    except Exception:
        return JSONResponse({"error": "invalid signature"}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_number = session.get("client_reference_id") or session.get("metadata", {}).get(
            "order_number"
        )
        if order_number:
            _mark_paid(order_number, session["id"])

    return JSONResponse({"received": True})


@router.post("/sslcommerz/ipn")
async def sslcommerz_ipn(request: Request):
    form = await request.form()
    val_id = form.get("val_id")
    tran_id = form.get("tran_id")
    status = form.get("status")

    if status == "VALID" and val_id and tran_id:
        validation = validate_sslcommerz_payment(val_id)
        if validation.get("status") in ("VALID", "VALIDATED"):
            _mark_paid(tran_id, val_id)
            return RedirectResponse(f"/orders/{tran_id}/thank-you", status_code=303)

    if tran_id:
        return RedirectResponse(f"/orders/{tran_id}", status_code=303)
    return JSONResponse({"received": True})
