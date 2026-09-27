import re
import time
import uuid

import markdown as md


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def generate_order_number() -> str:
    return f"MINA-{int(time.time())}{uuid.uuid4().hex[:4].upper()}"


def render_markdown(text: str) -> str:
    return md.markdown(text or "", extensions=["fenced_code", "tables", "nl2br"])
