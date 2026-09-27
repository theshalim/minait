"""Two Supabase clients:

- `supabase_admin`: uses the SERVICE ROLE key. Full read/write access, bypasses
  Row Level Security. Used by the backend for every database operation, since
  this code only ever runs on the server (Vercel serverless function), never
  in the browser.
- `supabase_auth`: uses the public ANON key, used only for the auth calls
  (sign up / sign in / sign out / get user) which is how Supabase Auth is
  designed to be used regardless of caller.
"""
from functools import lru_cache

from supabase import Client, create_client

from app.config import settings


@lru_cache
def get_admin_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@lru_cache
def get_auth_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


supabase_admin = get_admin_client
supabase_auth = get_auth_client
