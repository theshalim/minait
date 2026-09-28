from urllib.parse import parse_qs, unquote, urlparse

import app.security as security
from app.utils import unique_slug, whatsapp_number
from tests.conftest import login, make_token


def wa_text(location: str) -> str:
    return parse_qs(urlparse(location).query)["text"][0]


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
def test_home_renders_with_empty_database(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Mina IT Service" in r.text


def test_home_shows_bangla_content_when_filled_in(client, db):
    db.add("services", title="Web design", title_bn="ওয়েব ডিজাইন", slug="web-design", price=5000)
    db.add("services", title="Networking", slug="networking", price=3000)  # no Bangla copy
    db.add("site_stats", label="Clients", label_bn="ক্লায়েন্ট", value="10+")

    en = client.get("/").text
    assert "Web design" in en and "ওয়েব ডিজাইন" not in en

    client.cookies.set("lang", "bn")
    bn = client.get("/").text
    assert "ওয়েব ডিজাইন" in bn and "ক্লায়েন্ট" in bn
    assert "Networking" in bn  # falls back to English when no Bangla copy


def test_missing_service_order_and_post_are_404_not_500(client):
    assert client.get("/services/nope").status_code == 404
    assert client.get("/checkout/nope").status_code == 404
    assert client.get("/orders/MINA-NOPE").status_code == 404
    assert client.get("/blog/nope").status_code == 404


def test_set_lang_refuses_offsite_redirect(client):
    assert client.get("/set-lang/bn?next=//evil.com").headers["location"] == "/"
    assert client.get("/set-lang/bn?next=/blog").headers["location"] == "/blog"


def test_faq_api_answers_in_visitor_language(client, db):
    db.add("faqs", question="Price?", question_bn="দাম?", answer="Cheap", answer_bn="সস্তা")
    assert client.get("/api/faqs").json() == [{"question": "Price?", "answer": "Cheap"}]
    client.cookies.set("lang", "bn")
    assert client.get("/api/faqs").json() == [{"question": "দাম?", "answer": "সস্তা"}]


def test_assistant_widget_text_is_translated(client):
    client.cookies.set("lang", "bn")
    html = client.get("/").text
    assert "যেকোনো প্রশ্ন করুন" in html and "Ask us anything" not in html


def test_blog_post_uses_bangla_body(client, db):
    db.add("blog_posts", title="Hello", slug="hello", content_markdown="English body",
           content_markdown_bn="বাংলা লেখা", is_published=True)
    client.cookies.set("lang", "bn")
    assert "বাংলা লেখা" in client.get("/blog/hello").text


# ---------------------------------------------------------------------------
# Checkout & orders
# ---------------------------------------------------------------------------
def test_checkout_offers_only_configured_gateways_with_whatsapp_default(client, db, settings, monkeypatch):
    db.add("services", title="Repair", slug="repair", price=1000)
    html = client.get("/checkout/repair").text
    assert 'value="whatsapp" checked' in html
    assert 'value="stripe"' not in html and 'value="sslcommerz"' not in html

    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_123")
    html = client.get("/checkout/repair").text
    assert 'value="whatsapp" checked' in html and 'value="stripe"' in html


def _order_form(service_id, method="whatsapp"):
    return {"service_id": service_id, "customer_name": "Rahim", "customer_email": "r@example.com",
            "customer_phone": "01711111111", "payment_method": method}


def test_whatsapp_order_is_saved_and_opens_whatsapp(client, db):
    svc = db.add("services", title="Repair", slug="repair", price=1000)
    r = client.post("/orders", data=_order_form(svc["id"]))
    assert r.status_code == 303
    assert r.headers["location"].startswith("https://wa.me/8801700000000?text=")
    order = db.tables["orders"][0]
    assert order["order_number"] in wa_text(r.headers["location"])
    assert db.notifications and "New order" in db.notifications[0]


def test_unconfigured_gateway_falls_back_to_whatsapp(client, db):
    svc = db.add("services", title="Repair", slug="repair", price=1000)
    r = client.post("/orders", data=_order_form(svc["id"], method="stripe"))
    assert r.headers["location"].startswith("https://wa.me/")
    assert db.tables["orders"][0]["payment_method"] == "whatsapp"


def test_order_without_whatsapp_number_goes_to_status_page(client, db, settings, monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_NUMBER", "")
    svc = db.add("services", title="Repair", slug="repair", price=1000)
    r = client.post("/orders", data=_order_form(svc["id"]))
    assert r.headers["location"] == f"/orders/{db.tables['orders'][0]['order_number']}"


def test_order_status_page_is_translated(client, db):
    db.add("orders", order_number="MINA-1", service_title="Repair", customer_name="R",
           customer_email="r@x.com", amount=1000, currency="BDT", payment_method="whatsapp")
    client.cookies.set("lang", "bn")
    html = client.get("/orders/MINA-1?gateway_error=1").text
    for bangla in ("পরিমাণ", "অপেক্ষমাণ", "বাকি", "হোয়াটসঅ্যাপে মেসেজ দিন"):
        assert bangla in html
    for english in ("Amount", "Pending", "Unpaid", "A copy was sent"):
        assert english not in html


def test_telegram_message_escapes_customer_text(client, db):
    svc = db.add("services", title="Repair", slug="repair", price=1000)
    form = _order_form(svc["id"])
    form["customer_name"] = "<b>Tom & Jerry"
    client.post("/orders", data=form)
    assert "&lt;b&gt;Tom &amp; Jerry" in db.notifications[0]


# ---------------------------------------------------------------------------
# Login session refresh
# ---------------------------------------------------------------------------
def test_expired_access_token_is_refreshed(client, db, monkeypatch):
    db.add_user("user-1", "user@example.com")
    client.cookies.set("sb_access_token", make_token("user-1", expires_in=-10))
    client.cookies.set("sb_refresh_token", "refresh-old")
    calls = []

    def fake_refresh(token):
        calls.append(token)
        return {"access_token": make_token("user-1"), "refresh_token": "refresh-new"}

    monkeypatch.setattr(security, "refresh_tokens", fake_refresh)
    r = client.get("/dashboard")
    assert r.status_code == 200  # still logged in, not bounced to /login
    assert calls == ["refresh-old"]
    assert "refresh-new" in r.headers.get("set-cookie", "")


def test_valid_access_token_is_not_refreshed(client, db, monkeypatch):
    login(client, db)
    monkeypatch.setattr(security, "refresh_tokens", lambda t: (_ for _ in ()).throw(AssertionError))
    assert client.get("/dashboard").status_code == 200


def test_rejected_refresh_token_logs_out(client, db, monkeypatch):
    db.add_user("user-1", "user@example.com")
    client.cookies.set("sb_access_token", make_token("user-1", expires_in=-10))
    client.cookies.set("sb_refresh_token", "refresh-revoked")
    monkeypatch.setattr(security, "refresh_tokens", lambda t: None)
    r = client.get("/dashboard")
    assert r.status_code == 303 and r.headers["location"] == "/login"


def test_network_error_during_refresh_does_not_crash(client, db, monkeypatch):
    db.add_user("user-1", "user@example.com")
    client.cookies.set("sb_access_token", make_token("user-1", expires_in=-10))
    client.cookies.set("sb_refresh_token", "refresh-old")

    def boom(token):
        raise OSError("network down")

    monkeypatch.setattr(security, "refresh_tokens", boom)
    assert client.get("/").status_code == 200


def test_login_sets_cookies_and_opens_dashboard(client, db):
    db.add_user("user-1", "user@example.com", password="secret123")
    r = client.post("/login", data={"email": "user@example.com", "password": "secret123"})
    assert r.status_code == 303 and r.headers["location"] == "/dashboard"
    assert "sb_access_token" in r.headers.get("set-cookie", "")


def test_wrong_login_shows_translated_error(client, db):
    client.cookies.set("lang", "bn")
    r = client.post("/login", data={"email": "no@example.com", "password": "bad"})
    assert r.status_code == 401 and "ইমেইল বা পাসওয়ার্ড ভুল" in r.text


# ---------------------------------------------------------------------------
# Forgot / change password (no email involved)
# ---------------------------------------------------------------------------
def test_forgot_password_notifies_admin_and_opens_whatsapp(client, db):
    assert "/forgot-password" in client.get("/login").text
    r = client.post("/forgot-password", data={"email": "user@example.com"})
    assert r.headers["location"].startswith("https://wa.me/8801700000000")
    assert "user@example.com" in wa_text(r.headers["location"])
    assert "Password reset request" in db.notifications[0]


def test_forgot_password_without_whatsapp_shows_confirmation(client, db, settings, monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_NUMBER", "")
    r = client.post("/forgot-password", data={"email": "user@example.com"})
    assert r.status_code == 200 and "Request received" in r.text


def test_change_password_checks_current_password(client, db, monkeypatch):
    login(client, db)
    monkeypatch.setattr("app.routers.dashboard.check_password", lambda email, pw: pw == "secret123")

    r = client.post("/dashboard/password", data={"current_password": "wrong", "new_password": "newpass1"})
    assert "Current password is wrong" in r.text and not db.password_updates

    r = client.post("/dashboard/password", data={"current_password": "secret123", "new_password": "123"})
    assert "at least 6" in r.text and not db.password_updates

    r = client.post("/dashboard/password", data={"current_password": "secret123", "new_password": "newpass1"})
    assert "Password changed" in r.text
    assert db.password_updates == [("user-1", "newpass1")]


def test_check_password_calls_supabase_token_endpoint(monkeypatch, settings):
    seen = {}

    class Resp:
        def __init__(self, code):
            self.status_code = code

        def json(self):
            return {"access_token": "a", "refresh_token": "b"}

    def fake_post(url, params, headers, json, timeout):
        seen.update(url=url, params=params, body=json)
        return Resp(400 if json.get("password") == "wrong" else 200)

    monkeypatch.setattr(security.httpx, "post", fake_post)
    assert security.check_password("a@b.c", "right") is True
    assert seen["params"] == {"grant_type": "password"} and seen["url"].endswith("/auth/v1/token")
    assert security.check_password("a@b.c", "wrong") is False
    assert security.refresh_tokens("r") == {"access_token": "a", "refresh_token": "b"}


# ---------------------------------------------------------------------------
# Admin panel
# ---------------------------------------------------------------------------
def admin_login(client, db):
    login(client, db, uid="admin-1", email="admin@example.com", admin=True)


def test_admin_pages_need_admin(client, db):
    assert client.get("/admin").headers["location"] == "/login"
    login(client, db)
    assert client.get("/admin").status_code == 403


def test_all_admin_pages_render(client, db):
    admin_login(client, db)
    db.add("services", title="Repair", slug="repair", price=1000)
    db.add("orders", order_number="MINA-1", service_title="Repair", customer_name="R",
           customer_email="r@x.com", customer_phone="01711111111", amount=1000, currency="BDT",
           payment_method="whatsapp")
    for path in ("/admin", "/admin/home", "/admin/services", "/admin/services/new", "/admin/orders",
                 "/admin/users", "/admin/blog", "/admin/blog/new", "/admin/faqs"):
        assert client.get(path).status_code == 200, path


def test_same_title_twice_gets_unique_slugs(client, db):
    admin_login(client, db)
    form = {"title": "Web Design", "price": "100"}
    assert client.post("/admin/services/new", data=form).status_code == 303
    assert client.post("/admin/services/new", data=form).status_code == 303
    client.post("/admin/services/new", data={"title": "ওয়েব ডিজাইন", "price": "100"})
    client.post("/admin/services/new", data={"title": "নেটওয়ার্ক", "price": "100"})
    slugs = [s["slug"] for s in db.tables["services"]]
    assert slugs == ["web-design", "web-design-2", "service", "service-2"]

    post = {"title": "News", "content_markdown": "x"}
    client.post("/admin/blog/new", data=post)
    client.post("/admin/blog/new", data=post)
    assert [p["slug"] for p in db.tables["blog_posts"]] == ["news", "news-2"]


def test_admin_saves_bangla_fields(client, db):
    admin_login(client, db)
    client.post("/admin/services/new", data={"title": "Repair", "title_bn": "মেরামত",
                                             "description_bn": "বিবরণ", "price": "100"})
    svc = db.tables["services"][0]
    assert svc["title_bn"] == "মেরামত" and svc["description_bn"] == "বিবরণ"
    client.post("/admin/faqs/new", data={"question": "Q", "answer": "A", "question_bn": "প্র", "answer_bn": "উ"})
    assert db.tables["faqs"][0]["answer_bn"] == "উ"
    client.post("/admin/home/stats/new", data={"label": "Clients", "label_bn": "ক্লায়েন্ট", "value": "5"})
    assert db.tables["site_stats"][0]["label_bn"] == "ক্লায়েন্ট"


def test_admin_marks_whatsapp_order_paid_and_revenue_counts_it(client, db):
    admin_login(client, db)
    order = db.add("orders", order_number="MINA-1", service_title="Repair", customer_name="R",
                   customer_email="r@x.com", amount=1500, currency="BDT", payment_method="whatsapp")
    r = client.post(f"/admin/orders/{order['id']}/status",
                    data={"status": "in_progress", "payment_status": "paid", "back": "pending"})
    assert r.headers["location"] == f"/admin/orders?status=pending#order-{order['id']}"
    saved = db.tables["orders"][0]
    assert saved["status"] == "in_progress" and saved["payment_status"] == "paid"
    assert "1500" in client.get("/admin").text

    bad = client.post(f"/admin/orders/{order['id']}/status", data={"status": "done", "payment_status": "paid"})
    assert bad.status_code == 400


def test_admin_orders_have_whatsapp_customer_button(client, db):
    admin_login(client, db)
    db.add("orders", order_number="MINA-7", service_title="Repair", customer_name="Karim",
           customer_email="k@x.com", customer_phone="01812-345678", amount=1000, currency="BDT",
           payment_method="whatsapp", status="completed", payment_status="paid")
    html = client.get("/admin/orders").text
    assert "https://wa.me/8801812345678?text=" in html
    link = html.split('href="https://wa.me/8801812345678?text=')[1].split('"')[0]
    text = unquote(link.replace("&amp;", "&"))
    assert "MINA-7" in text and "সম্পন্ন" in text and "Completed" in text
    assert "https://mina.test/orders/MINA-7" in text


def test_slide_can_be_hidden_and_shown(client, db):
    admin_login(client, db)
    slide = db.add("hero_slides", image_url="https://img/1.jpg", heading="")
    assert "https://img/1.jpg" in client.get("/").text
    client.post(f"/admin/home/slides/{slide['id']}/toggle")
    assert db.tables["hero_slides"][0]["is_active"] is False
    assert "https://img/1.jpg" not in client.get("/").text
    client.post(f"/admin/home/slides/{slide['id']}/toggle")
    assert "https://img/1.jpg" in client.get("/").text


def test_admin_sets_customer_password(client, db):
    admin_login(client, db)
    db.add_user("user-9", "cust@example.com", phone="01999999999")
    html = client.get("/admin/users").text
    assert "cust@example.com" in html

    r = client.post("/admin/users/user-9/password", data={"new_password": "temp1234"})
    assert "Password updated" in r.text
    assert db.password_updates == [("user-9", "temp1234")]
    assert "https://wa.me/8801999999999?text=" in r.text

    r = client.post("/admin/users/user-9/password", data={"new_password": "123"})
    assert "at least 6" in r.text and len(db.password_updates) == 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def test_whatsapp_number_normalisation():
    assert whatsapp_number("01712-345678") == "8801712345678"
    assert whatsapp_number("+880 1712 345678") == "8801712345678"
    assert whatsapp_number("1712345678") == "8801712345678"
    assert whatsapp_number("") == "" and whatsapp_number(None) == "" and whatsapp_number("123") == ""


def test_unique_slug():
    taken = {"a", "a-2"}
    assert unique_slug("A", "x", taken.__contains__) == "a-3"
    assert unique_slug("বাংলা", "service", taken.__contains__) == "service"


# ---------------------------------------------------------------------------
# Blog page: top post, share buttons, search, pages
# ---------------------------------------------------------------------------
def _posts(db, n, **extra):
    return [db.add("blog_posts", title=f"Post {i}", slug=f"post-{i}", excerpt=f"About {i}",
                   content_markdown="x", is_published=True, created_at=f"2026-08-{i:02d}T10:00:00", **extra)
            for i in range(1, n + 1)]


def _top_title(html):
    return html.split("<article")[1].split("</h2>")[0].rsplit(">", 1)[1]


def test_blog_newest_post_is_on_top_by_default(client, db):
    _posts(db, 3)
    html = client.get("/blog").text
    assert _top_title(html) == "Post 3"
    assert "August 3, 2026" in html


def test_admin_picks_the_top_post(client, db):
    posts = _posts(db, 3)
    admin_login(client, db)
    client.post(f"/admin/blog/{posts[0]['id']}/feature")
    assert _top_title(client.get("/blog").text) == "Post 1"
    assert "★ Top post" in client.get("/admin/blog").text

    client.post(f"/admin/blog/{posts[1]['id']}/feature")  # only one top post at a time
    assert [p["is_featured"] for p in db.tables["blog_posts"]] == [False, True, False]
    client.post(f"/admin/blog/{posts[1]['id']}/feature")  # un-pick -> newest again
    assert _top_title(client.get("/blog").text) == "Post 3"


def test_blog_share_buttons(client, db):
    _posts(db, 1)
    html = client.get("/blog").text
    url = "https%3A//mina.test/blog/post-1"
    assert f"facebook.com/sharer/sharer.php?u={url}" in html
    assert f"twitter.com/intent/tweet?url={url}" in html
    assert f"linkedin.com/sharing/share-offsite/?url={url}" in html
    assert "mail.google.com/mail/?view=cm" in html
    assert 'data-share-url="https://mina.test/blog/post-1"' in html
    assert "facebook.com/sharer" in client.get("/blog/post-1").text


def test_blog_search_and_pages(client, db):
    _posts(db, 23)
    page1 = client.get("/blog").text
    assert page1.count("<article") == 11  # top post + 10
    assert 'href="/blog?page=3"' in page1
    page3 = client.get("/blog?page=3").text
    assert page3.count("<article") == 2  # posts 2 and 1, no top post
    found = client.get("/blog?q=about 7").text
    assert found.count("<article") == 1 and "Post 7" in found
    assert "No articles match" in client.get("/blog?q=zzz").text


def test_blog_dates_in_bangla(client, db):
    _posts(db, 1)
    client.cookies.set("lang", "bn")
    html = client.get("/blog").text
    assert "১ আগস্ট, ২০২৬" in html and "বিস্তারিত পড়ুন" in html
