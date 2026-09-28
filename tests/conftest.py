"""Test setup: the whole app runs against an in-memory fake of Supabase, so
tests need no internet, no keys and no real database.

`FakeSupabase` implements only the small slice of the SDK this app uses:
table().select/eq/order/limit/maybe_single/insert/update/delete/upsert
.execute(), plus auth.get_user / sign_up / sign_in_with_password and
auth.admin.list_users / update_user_by_id.
"""
import base64
import itertools
import json
import time
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.supabase_client as supabase_client


def make_token(user_id: str, expires_in: int = 3600) -> str:
    """A JWT-shaped token the fake auth understands (not signed)."""
    payload = json.dumps({"sub": user_id, "exp": int(time.time()) + expires_in}).encode()
    return "h." + base64.urlsafe_b64encode(payload).decode().rstrip("=") + ".s"


def _token_payload(token: str) -> dict:
    part = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))


DEFAULTS = {
    "services": {"is_active": True, "sort_order": 0, "currency": "BDT", "category": "General", "description": ""},
    "hero_slides": {"is_active": True, "sort_order": 0},
    "blog_posts": {"is_published": False},
    "orders": {"payment_status": "unpaid", "status": "pending"},
    "profiles": {"is_admin": False},
    "faqs": {"sort_order": 0},
    "site_stats": {"sort_order": 0},
}


class Query:
    def __init__(self, db, table):
        self.db, self.table = db, table
        self.filters, self.orders = [], []
        self.op, self.payload, self.cols, self.count = "select", None, "*", None
        self.single, self.max = False, None

    # --- builders ---
    def select(self, cols="*", count=None):
        self.cols, self.count = cols, count
        return self

    def eq(self, col, value):
        self.filters.append((col, value))
        return self

    def order(self, col, desc=False):
        self.orders.append((col, desc))
        return self

    def limit(self, n):
        self.max = n
        return self

    def maybe_single(self):
        self.single = True
        return self

    def insert(self, data):
        self.op, self.payload = "insert", data
        return self

    def upsert(self, data, on_conflict="id"):
        self.op, self.payload, self.conflict = "upsert", data, on_conflict
        return self

    def update(self, data):
        self.op, self.payload = "update", data
        return self

    def delete(self):
        self.op = "delete"
        return self

    # --- execution ---
    def _matches(self, row):
        return all(str(row.get(c)) == str(v) for c, v in self.filters)

    def execute(self):
        rows = self.db.tables.setdefault(self.table, [])
        if self.op == "insert":
            items = self.payload if isinstance(self.payload, list) else [self.payload]
            out = []
            for item in items:
                if "slug" in item and any(r.get("slug") == item["slug"] for r in rows):
                    raise Exception('duplicate key value violates unique constraint "slug"')
                row = {**DEFAULTS.get(self.table, {}), **item}
                row.setdefault("id", next(self.db.ids))
                row.setdefault("created_at", f"2026-09-{len(rows) + 1:02d}T10:00:00")
                rows.append(row)
                out.append(dict(row))
            return SimpleNamespace(data=out, count=None)
        if self.op == "upsert":
            existing = next((r for r in rows if r.get(self.conflict) == self.payload[self.conflict]), None)
            if existing:
                existing.update(self.payload)
                return SimpleNamespace(data=[dict(existing)], count=None)
            self.op = "insert"
            return self.execute()
        matched = [r for r in rows if self._matches(r)]
        if self.op == "update":
            for r in matched:
                r.update(self.payload)
            return SimpleNamespace(data=[dict(r) for r in matched], count=None)
        if self.op == "delete":
            self.db.tables[self.table] = [r for r in rows if r not in matched]
            return SimpleNamespace(data=[dict(r) for r in matched], count=None)

        for col, desc in reversed(self.orders):
            matched.sort(key=lambda r: (r.get(col) is None, r.get(col)), reverse=desc)
        if self.max is not None:
            matched = matched[: self.max]
        if self.cols != "*":
            wanted = [c.strip() for c in self.cols.split(",")]
            matched = [{c: r.get(c) for c in wanted} for r in matched]
        else:
            matched = [dict(r) for r in matched]
        if self.single:
            return SimpleNamespace(data=matched[0], count=None) if matched else None
        return SimpleNamespace(data=matched, count=len(matched) if self.count else None)


class FakeAdminAuth:
    def __init__(self, db):
        self.db = db

    def list_users(self, page=None, per_page=None):
        return [SimpleNamespace(id=u["id"], email=u["email"], created_at=u["created_at"]) for u in self.db.users.values()]

    def update_user_by_id(self, uid, attrs):
        self.db.users[uid].update(attrs)
        self.db.password_updates.append((uid, attrs.get("password")))


class FakeAuth:
    def __init__(self, db):
        self.db = db
        self.admin = FakeAdminAuth(db)

    def get_user(self, token):
        payload = _token_payload(token)
        if payload["exp"] < time.time():
            raise Exception("JWT expired")
        u = self.db.users.get(payload["sub"])
        return SimpleNamespace(user=SimpleNamespace(id=u["id"], email=u["email"]) if u else None)

    def _session(self, uid):
        return SimpleNamespace(access_token=make_token(uid), refresh_token=f"refresh-{uid}")

    def sign_up(self, creds):
        uid = f"user-{len(self.db.users) + 1}"
        self.db.add_user(uid, creds["email"], creds["password"])
        return SimpleNamespace(user=SimpleNamespace(id=uid, email=creds["email"]), session=self._session(uid))

    def sign_in_with_password(self, creds):
        for u in self.db.users.values():
            if u["email"] == creds["email"] and u["password"] == creds["password"]:
                return SimpleNamespace(user=SimpleNamespace(id=u["id"]), session=self._session(u["id"]))
        raise Exception("Invalid login credentials")


class FakeSupabase:
    def __init__(self):
        self.tables = {}
        self.users = {}
        self.password_updates = []
        self.ids = itertools.count(1)
        self.auth = FakeAuth(self)

    def table(self, name):
        return Query(self, name)

    def add_user(self, uid, email, password="secret123", admin=False, full_name="Test User", phone=""):
        self.users[uid] = {"id": uid, "email": email, "password": password, "created_at": "2026-09-01T00:00:00"}
        self.tables.setdefault("profiles", []).append(
            {"id": uid, "full_name": full_name, "phone": phone, "is_admin": admin}
        )

    def add(self, table, **row):
        return self.table(table).insert(row).execute().data[0]


@pytest.fixture
def db(monkeypatch):
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "create_client", lambda *a, **k: fake)
    supabase_client.get_admin_client.cache_clear()
    supabase_client.get_auth_client.cache_clear()
    # Outgoing notifications must never hit the network in tests.
    sent = []
    import app.notify as notify

    monkeypatch.setattr(notify, "_send_telegram", sent.append)
    monkeypatch.setattr(notify, "_send_discord", lambda text: None)
    fake.notifications = sent
    yield fake
    supabase_client.get_admin_client.cache_clear()
    supabase_client.get_auth_client.cache_clear()


@pytest.fixture
def settings(monkeypatch):
    from app.config import settings as s

    for name, value in {
        "WHATSAPP_NUMBER": "8801700000000",
        "STRIPE_SECRET_KEY": "",
        "SSLCOMMERZ_STORE_ID": "",
        "SSLCOMMERZ_STORE_PASSWORD": "",
        "SITE_URL": "https://mina.test",
    }.items():
        monkeypatch.setattr(s, name, value)
    return s


@pytest.fixture
def client(db, settings):
    from app.main import app

    # https, because the session cookies are Secure-only.
    with TestClient(app, base_url="https://testserver", follow_redirects=False) as c:
        yield c


def login(client, db, uid="user-1", email="user@example.com", **profile):
    if uid not in db.users:
        db.add_user(uid, email, **profile)
    client.cookies.set("sb_access_token", make_token(uid))
    client.cookies.set("sb_refresh_token", f"refresh-{uid}")
