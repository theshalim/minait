import re
import time
import uuid
from urllib.parse import quote

import markdown as md


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def unique_slug(title: str, fallback: str, is_taken) -> str:
    """slugify(title), made unique by adding -2, -3, ... when `is_taken(slug)`
    says it's already used. A title with no English letters (e.g. written
    only in Bangla) slugifies to nothing, so `fallback` ("service", "post")
    is used as the base instead."""
    base = slugify(title) or fallback
    slug, n = base, 1
    while is_taken(slug):
        n += 1
        slug = f"{base}-{n}"
    return slug


def generate_order_number() -> str:
    return f"MINA-{int(time.time())}{uuid.uuid4().hex[:4].upper()}"


def render_markdown(text: str) -> str:
    return md.markdown(text or "", extensions=["fenced_code", "tables", "nl2br"])


def whatsapp_number(phone: str | None) -> str:
    """Turns what customers type ("01712-345678", "+880 1712 345678") into
    the digits-only international form wa.me needs ("8801712345678").
    Returns "" when there's nothing usable."""
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("01") and len(digits) == 11:  # local Bangladeshi mobile
        return "88" + digits
    if digits.startswith("1") and len(digits) == 10:  # local, leading 0 dropped
        return "880" + digits
    return digits if len(digits) >= 8 else ""


def whatsapp_link(number: str, text: str = "") -> str:
    return f"https://wa.me/{number}" + (f"?text={quote(text)}" if text else "")
