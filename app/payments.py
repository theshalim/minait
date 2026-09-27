"""Payment gateway integrations.

Both gateways are pay-per-transaction (no fixed monthly fee), matching the
project's cost constraint:

- Stripe: for international cards. Uses Stripe Checkout (hosted page), the
  simplest and most secure integration (no card data ever touches our server).
- SSLCOMMERZ: for Bangladeshi bKash/Nagad/Rocket/cards. Uses their hosted
  gateway too — we call their REST API to get a GatewayPageURL and redirect
  the customer there.
"""
import httpx
import stripe

from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

SSLCOMMERZ_SESSION_URL = (
    "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
    if settings.SSLCOMMERZ_SANDBOX
    else "https://securepay.sslcommerz.com/gwprocess/v4/api.php"
)
SSLCOMMERZ_VALIDATION_URL = (
    "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
    if settings.SSLCOMMERZ_SANDBOX
    else "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"
)


def create_stripe_checkout_session(order: dict) -> str:
    """Creates a Stripe Checkout Session and returns its hosted URL."""
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": order["currency"].lower(),
                    "product_data": {"name": order["service_title"]},
                    "unit_amount": int(round(float(order["amount"]) * 100)),
                },
                "quantity": 1,
            }
        ],
        customer_email=order["customer_email"],
        client_reference_id=order["order_number"],
        success_url=f"{settings.SITE_URL}/orders/{order['order_number']}/thank-you?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.SITE_URL}/orders/{order['order_number']}",
        metadata={"order_number": order["order_number"]},
    )
    return session.url


def create_sslcommerz_session(order: dict) -> str:
    """Initiates an SSLCOMMERZ session and returns the GatewayPageURL."""
    payload = {
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
        "total_amount": str(order["amount"]),
        "currency": order["currency"],
        "tran_id": order["order_number"],
        "success_url": f"{settings.SITE_URL}/webhooks/sslcommerz/ipn",
        "fail_url": f"{settings.SITE_URL}/orders/{order['order_number']}",
        "cancel_url": f"{settings.SITE_URL}/orders/{order['order_number']}",
        "cus_name": order["customer_name"],
        "cus_email": order["customer_email"],
        "cus_phone": order.get("customer_phone") or "N/A",
        "cus_add1": "N/A",
        "cus_city": "N/A",
        "cus_country": "Bangladesh",
        "shipping_method": "NO",
        "product_name": order["service_title"],
        "product_category": "Service",
        "product_profile": "general",
    }
    resp = httpx.post(SSLCOMMERZ_SESSION_URL, data=payload, timeout=15)
    data = resp.json()
    if data.get("status") != "SUCCESS":
        raise RuntimeError(f"SSLCOMMERZ session failed: {data.get('failedreason', data)}")
    return data["GatewayPageURL"]


def validate_sslcommerz_payment(val_id: str) -> dict:
    """Server-to-server validation of an SSLCOMMERZ transaction (required —
    never trust the redirect alone)."""
    params = {
        "val_id": val_id,
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
        "format": "json",
    }
    resp = httpx.get(SSLCOMMERZ_VALIDATION_URL, params=params, timeout=15)
    return resp.json()


def retrieve_stripe_session(session_id: str):
    return stripe.checkout.Session.retrieve(session_id)


def construct_stripe_webhook_event(payload: bytes, sig_header: str):
    return stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
