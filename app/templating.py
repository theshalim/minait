from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.security import get_optional_user

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def base_ctx(request: Request, **extra) -> dict:
    """Common context every template needs: the request itself (required by
    Jinja2Templates), the logged-in user (or None), and site settings."""
    ctx = {
        "request": request,
        "user": get_optional_user(request),
        "site_name": settings.SITE_NAME,
        "whatsapp_number": settings.WHATSAPP_NUMBER,
    }
    ctx.update(extra)
    return ctx
