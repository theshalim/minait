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

KEYS = ("contact_email", "contact_phone")
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


def save_site_settings(values: dict) -> None:
    for key in KEYS:
        if key in values:
            supabase_admin().table("site_settings").upsert(
                {"key": key, "value": values[key].strip()}, on_conflict="key"
            ).execute()
    _cache["at"] = 0.0  # show the change right away
