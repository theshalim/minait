from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.i18n import format_date, get_locale, localized, make_translator
from app.security import get_optional_user
from app.site_settings import get_site_settings

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def base_ctx(request: Request, **extra) -> dict:
    """Common context every template needs: the request itself (required by
    Jinja2Templates), the logged-in user (or None), site settings, and the
    current language with its t() translator and loc() content picker."""
    lang = get_locale(request)
    ctx = {
        "request": request,
        "user": get_optional_user(request),
        "site_name": settings.SITE_NAME,
        "whatsapp_number": settings.WHATSAPP_NUMBER,
        "site_url": settings.SITE_URL.rstrip("/"),
        "contact": get_site_settings(),
        "lang": lang,
        "t": make_translator(lang),
        "loc": lambda row, field: localized(row, field, lang),
        "fmt_date": lambda value: format_date(value, lang),
    }
    ctx.update(extra)
    return ctx
