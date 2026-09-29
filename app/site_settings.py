"""Small admin-editable site settings (e.g. the contact email and phone in
the footer), stored as key/value rows in the `site_settings` table.

Every page shows them, so they're cached in memory for a minute instead of
being fetched on each request. A missing table (db/schema.sql not re-run
yet) just means "no settings".
"""
import logging
import time

from app.supabase_client import supabase_admin

logger = logging.getLogger("minait")

KEYS = (
    "contact_email",
    "contact_phone",
    "products_slide_seconds",
    "services_slide_seconds",
    "services_hero_image",
    "tech_stack",
)
_CACHE_SECONDS = 60
_cache: dict = {"at": 0.0, "values": {}}


def get_site_settings() -> dict:
    if time.time() - _cache["at"] < _CACHE_SECONDS:
        return _cache["values"]
    try:
        rows = supabase_admin().table("site_settings").select("*").execute().data
        values = {r["key"]: r["value"] or "" for r in rows}
    except Exception:
        logger.exception("Couldn't load site settings")
        values = {}
    _cache.update(at=time.time(), values=values)
    return values


# About page texts (Admin -> About page). Each has an English key
# "about_<field>" and a Bangla one "about_<field>_bn"; the picture has one.
ABOUT_TEXT_FIELDS = (
    "hero_title", "hero_text", "hero_text2", "features_heading", "story_heading",
    "story_text", "numbers_heading", "numbers_text", "cta_heading", "cta_text",
)
ABOUT_KEYS = tuple(
    [f"about_{f}" for f in ABOUT_TEXT_FIELDS]
    + [f"about_{f}_bn" for f in ABOUT_TEXT_FIELDS]
    + ["about_story_image"]
)


def about_texts(contact: dict, lang: str, t) -> dict:
    """The About page's texts in the visitor's language: what the admin
    wrote, else the built-in default."""
    out = {}
    for f in ABOUT_TEXT_FIELDS:
        english = contact.get(f"about_{f}") or ""
        if lang == "bn":
            # Bangla text if written; else the admin's own English (their
            # facts beat a generic default); else the built-in Bangla.
            out[f] = contact.get(f"about_{f}_bn") or english or t(f"about.{f}")
        else:
            out[f] = english or t(f"about.{f}")
    return out


def save_site_settings(values: dict) -> None:
    for key in KEYS + ABOUT_KEYS:
        if key in values:
            supabase_admin().table("site_settings").upsert(
                {"key": key, "value": values[key].strip()}, on_conflict="key"
            ).execute()
    _cache["at"] = 0.0  # show the change right away
