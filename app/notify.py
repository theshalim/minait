"""Instant admin notifications via Telegram Bot API and/or Discord webhook.

Fires on: a visitor's order / demo request, payment received. Failures here must never break
the request that triggered them, so every call is best-effort and swallows
its own errors.
"""
from html import escape

import httpx

from app.config import settings


def _send_telegram(text: str) -> None:
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        httpx.post(
            url,
            json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=5,
        )
    except Exception:
        pass


def _send_discord(text: str) -> None:
    if not settings.DISCORD_WEBHOOK_URL:
        return
    try:
        httpx.post(settings.DISCORD_WEBHOOK_URL, json={"content": text}, timeout=5)
    except Exception:
        pass


def notify_admin(text: str) -> None:
    _send_telegram(text)
    _send_discord(text)


def _clean(order: dict) -> dict:
    # Messages are sent as Telegram HTML: a customer typing "<" or "&" in
    # their name would otherwise make Telegram reject the whole message.
    return {k: escape(str(v)) if v is not None else None for k, v in order.items()}


def notify_new_request(order: dict) -> None:
    """A visitor sent the website's Order / Book-a-demo form."""
    order = _clean(order)
    label = "Demo request" if order.get("kind") == "demo" else "New order request"
    text = (
        f"🆕 <b>{label} — {order['order_number']}</b>\n"
        f"For: {order['service_title']}\n"
        f"Name: {order['customer_name']}\n"
        f"Email: {order.get('customer_email') or '-'}\n"
        f"Phone: {order.get('customer_phone') or '-'}\n"
        f"Message: {order.get('notes') or '-'}"
    )
    notify_admin(text)


def notify_payment_received(order: dict) -> None:
    order = _clean(order)
    text = (
        f"💰 <b>Payment received — {order['order_number']}</b>\n"
        f"Service: {order['service_title']}\n"
        f"Amount: {order['amount']} {order['currency']}\n"
        f"Ref: {order.get('payment_ref') or '-'}"
    )
    notify_admin(text)
