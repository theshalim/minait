"""Instant admin notifications via Telegram Bot API and/or Discord webhook.

Fires on: new order placed, payment received. Failures here must never break
the request that triggered them, so every call is best-effort and swallows
its own errors.
"""
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


def notify_new_order(order: dict) -> None:
    text = (
        f"🆕 <b>New order — {order['order_number']}</b>\n"
        f"Service: {order['service_title']}\n"
        f"Customer: {order['customer_name']} ({order['customer_email']})\n"
        f"Phone: {order.get('customer_phone') or '-'}\n"
        f"Amount: {order['amount']} {order['currency']}\n"
        f"Payment method: {order['payment_method']}"
    )
    notify_admin(text)


def notify_payment_received(order: dict) -> None:
    text = (
        f"💰 <b>Payment received — {order['order_number']}</b>\n"
        f"Service: {order['service_title']}\n"
        f"Amount: {order['amount']} {order['currency']}\n"
        f"Ref: {order.get('payment_ref') or '-'}"
    )
    notify_admin(text)
