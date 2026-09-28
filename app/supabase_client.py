"""Two Supabase clients:

- `supabase_admin`: uses the SERVICE ROLE key. Full read/write access, bypasses
  Row Level Security. Used by the backend for every database operation, since
  this code only ever runs on the server (Vercel serverless function), never
  in the browser.
- `supabase_auth`: uses the public ANON key, used only for the auth calls
  (sign up / sign in / get user) which is how Supabase Auth is designed to be
  used regardless of caller.

Both are shared by every visitor, so neither may keep or auto-refresh a
session of its own — per-visitor sessions live in cookies (see security.py).
"""
from functools import lru_cache

from supabase import Client, ClientOptions, create_client

from app.config import settings

_OPTIONS = dict(auto_refresh_token=False, persist_session=False)


@lru_cache
def get_admin_client() -> Client:
    return create_client(
        settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY, options=ClientOptions(**_OPTIONS)
    )


@lru_cache
def get_auth_client() -> Client:
    return create_client(
        settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY, options=ClientOptions(**_OPTIONS)
    )


supabase_admin = get_admin_client
supabase_auth = get_auth_client


def fetch_one(query) -> dict | None:
    """Runs `query.maybe_single()` and returns the row or None. (The SDK's
    maybe_single().execute() returns None itself — not a response with
    empty data — when nothing matches, so `.execute().data` would crash.)"""
    res = query.maybe_single().execute()
    return res.data if res else None
