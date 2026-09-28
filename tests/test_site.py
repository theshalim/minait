"""One admin, no customer accounts, WhatsApp ordering, products, clients."""
from urllib.parse import unquote

import app.security as security
from tests.conftest import login, make_token
from tests.test_app import admin_login, wa_text


def wa_link_text(html: str, number: str = "8801700000000") -> str:
    link = html.split(f'href="https://wa.me/{number}?text=')[1].split('"')[0]
    return unquote(link.replace("&amp;", "&"))


# ---------------------------------------------------------------------------
# Public site
# ---------------------------------------------------------------------------
def test_public_navbar_has_no_account_links(client, db):
    admin_login(client, db)  # even when the admin is logged in
    html = client.get("/").text
    for link in ('href="/admin"', 'href="/login"', 'href="/signup"', 'href="/dashboard"', 'href="/logout"'):
        assert link not in html
    assert 'href="/products"' in html and 'id="menu-toggle"' in html


def test_signup_and_dashboard_are_gone(client, db):
    assert client.get("/signup").headers["location"] == "/login"
    assert client.get("/dashboard").headers["location"] == "/admin"


def test_order_buttons_open_whatsapp_with_the_item(client, db):
    db.add("services", title="Repair", slug="repair", price=1500)
    html = client.get("/services").text
    text = wa_link_text(html)
    assert "Repair" in text and "1,500 BDT" in text
    assert "/checkout/" not in html


def test_old_checkout_link_redirects_to_whatsapp(client, db):
    db.add("services", title="Repair", title_bn="মেরামত", slug="repair", price=1500)
    r = client.get("/checkout/repair")
    assert r.headers["location"].startswith("https://wa.me/8801700000000?text=")
    client.cookies.set("lang", "bn")
    assert "মেরামত" in wa_text(client.get("/checkout/repair").headers["location"])
    assert client.post("/orders", data={}).status_code in (404, 405)  # no public order form any more


def test_services_page_and_detail(client, db):
    db.add("services", title="Networking", slug="networking", price=3000, category="Office", description="LAN")
    html = client.get("/services").text
    assert "Networking" in html and "Office" in html
    detail = client.get("/services/networking")
    assert detail.status_code == 200 and "wa.me" in detail.text


def test_products_page(client, db):
    db.add("products", title="Router", title_bn="রাউটার", slug="router", price=2500)
    db.add("products", title="Custom PC", slug="custom-pc", price=None)
    db.add("products", title="Old stock", slug="old", price=1, is_active=False)
    html = client.get("/products").text
    assert "Router" in html and "2,500 BDT" in html
    assert "Price on request" in html and "Old stock" not in html
    client.cookies.set("lang", "bn")
    assert "রাউটার" in client.get("/products").text


def test_pages_survive_missing_new_tables(client, db):
    db.missing_tables |= {"products", "testimonials", "clients"}
    assert client.get("/").status_code == 200
    assert client.get("/products").status_code == 200


def test_home_shows_testimonials_and_moving_client_logos(client, db):
    db.add("testimonials", name="Rahim Uddin", role="CEO, ABC", message="Great service!", message_bn="দারুণ সার্ভিস!")
    db.add("testimonials", name="Hidden Person", message="x", is_active=False)
    db.add("clients", name="ABC Traders", logo_url="https://img/abc.png")
    html = client.get("/").text
    assert "Great service!" in html and "Rahim Uddin" in html and "CEO, ABC" in html
    assert "Hidden Person" not in html
    assert 'class="marquee-track"' in html and html.count("https://img/abc.png") >= 16  # repeated to loop
    client.cookies.set("lang", "bn")
    assert "দারুণ সার্ভিস!" in client.get("/").text


def test_home_services_subtitle_removed(client, db):
    client.cookies.set("lang", "bn")
    assert "লুকোচুরি" not in client.get("/").text


# ---------------------------------------------------------------------------
# Admin login
# ---------------------------------------------------------------------------
def test_login_opens_admin(client, db):
    db.add_user("admin-1", "admin@example.com", password="secret123", admin=True)
    r = client.post("/login", data={"email": "admin@example.com", "password": "secret123"})
    assert r.status_code == 303 and r.headers["location"] == "/admin"
    assert "sb_access_token" in r.headers.get("set-cookie", "")
    assert "/signup" not in client.get("/login").text


def test_expired_access_token_is_refreshed(client, db, monkeypatch):
    db.add_user("admin-1", "admin@example.com", admin=True)
    client.cookies.set("sb_access_token", make_token("admin-1", expires_in=-10))
    client.cookies.set("sb_refresh_token", "refresh-old")
    calls = []

    def fake_refresh(token):
        calls.append(token)
        return {"access_token": make_token("admin-1"), "refresh_token": "refresh-new"}

    monkeypatch.setattr(security, "refresh_tokens", fake_refresh)
    r = client.get("/admin")
    assert r.status_code == 200  # still logged in, not bounced to /login
    assert calls == ["refresh-old"]
    assert "refresh-new" in r.headers.get("set-cookie", "")


def test_valid_access_token_is_not_refreshed(client, db, monkeypatch):
    admin_login(client, db)
    monkeypatch.setattr(security, "refresh_tokens", lambda t: (_ for _ in ()).throw(AssertionError))
    assert client.get("/admin").status_code == 200


def test_non_admin_cannot_open_admin(client, db):
    login(client, db)
    assert client.get("/admin").status_code == 403


# ---------------------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------------------
def test_all_admin_pages_render(client, db):
    admin_login(client, db)
    db.add("services", title="Repair", slug="repair", price=1000)
    db.add("products", title="Router", slug="router", price=2500)
    db.add("testimonials", name="Rahim", message="Nice")
    db.add("clients", name="ABC", logo_url="https://img/abc.png")
    db.add("orders", order_number="MINA-1", service_title="Repair", customer_name="R",
           customer_email="", customer_phone="01711111111", amount=1000, currency="BDT",
           payment_method="whatsapp")
    product_id = db.tables["products"][0]["id"]
    for path in ("/admin", "/admin/home", "/admin/services", "/admin/services/new", "/admin/products",
                 "/admin/products/new", f"/admin/products/{product_id}/edit", "/admin/orders",
                 "/admin/clients", "/admin/account", "/admin/blog", "/admin/blog/new", "/admin/faqs"):
        assert client.get(path).status_code == 200, path


def test_admin_product_crud(client, db):
    admin_login(client, db)
    client.post("/admin/products/new", data={"title": "Router", "title_bn": "রাউটার", "price": "2500"})
    client.post("/admin/products/new", data={"title": "Router", "price": ""})
    rows = db.tables["products"]
    assert [p["slug"] for p in rows] == ["router", "router-2"]
    assert rows[0]["price"] == 2500.0 and rows[1]["price"] is None
    pid = rows[0]["id"]
    client.post(f"/admin/products/{pid}/edit", data={"title": "Wi-Fi Router", "price": "2700"})
    assert db.tables["products"][0]["title"] == "Wi-Fi Router"
    client.post(f"/admin/products/{pid}/toggle")
    assert db.tables["products"][0]["is_active"] is False
    client.post(f"/admin/products/{pid}/delete")
    assert len(db.tables["products"]) == 1


def test_admin_manages_testimonials_and_logos(client, db):
    admin_login(client, db)
    client.post("/admin/clients/testimonials/new",
                data={"name": "Rahim", "role": "CEO", "message": "Great", "message_bn": "দারুণ"})
    tid = db.tables["testimonials"][0]["id"]
    client.post(f"/admin/clients/testimonials/{tid}/edit", data={"name": "Rahim U.", "message": "Great!"})
    assert db.tables["testimonials"][0]["name"] == "Rahim U."
    client.post(f"/admin/clients/testimonials/{tid}/toggle")
    assert db.tables["testimonials"][0]["is_active"] is False
    client.post(f"/admin/clients/testimonials/{tid}/delete")
    assert db.tables["testimonials"] == []

    client.post("/admin/clients/logos/new", data={"name": "ABC", "logo_url": "https://img/abc.png"})
    cid = db.tables["clients"][0]["id"]
    assert "https://img/abc.png" in client.get("/admin/clients").text
    client.post(f"/admin/clients/logos/{cid}/delete")
    assert db.tables["clients"] == []


def test_admin_changes_own_password(client, db, monkeypatch):
    admin_login(client, db)
    monkeypatch.setattr("app.routers.admin.check_password", lambda email, pw: pw == "oldpass123")
    form = {"current_password": "wrong", "new_password": "newpass123", "confirm_password": "newpass123"}
    assert "current password is wrong" in client.post("/admin/account/password", data=form).text
    form.update(current_password="oldpass123", confirm_password="different1")
    assert "match" in client.post("/admin/account/password", data=form).text
    form.update(new_password="short", confirm_password="short")
    assert "at least 8" in client.post("/admin/account/password", data=form).text
    assert not db.password_updates
    form.update(new_password="newpass123", confirm_password="newpass123")
    assert "Password changed" in client.post("/admin/account/password", data=form).text
    assert db.password_updates == [("admin-1", "newpass123")]


def test_admin_adds_chat_order_manually(client, db):
    admin_login(client, db)
    db.add("services", title="Repair", slug="repair", price=1000)
    assert '<option value="Repair">' in client.get("/admin/orders").text
    r = client.post("/admin/orders/new", data={"customer_name": "Karim", "customer_phone": "01812345678",
                                               "service_title": "Repair", "amount": "1200",
                                               "payment_status": "paid", "status": "in_progress"})
    order = db.tables["orders"][0]
    assert r.headers["location"] == f"/admin/orders#order-{order['id']}"
    assert order["order_number"].startswith("MINA-") and order["payment_method"] == "whatsapp"
    assert order["amount"] == 1200.0 and order["payment_status"] == "paid"
    assert "1,200 BDT" in client.get("/admin").text  # counted in revenue
    assert client.get(f"/orders/{order['order_number']}").status_code == 200  # tracking link works
    client.post(f"/admin/orders/{order['id']}/delete")
    assert db.tables["orders"] == []


# ---------------------------------------------------------------------------
# Footer contact, less WhatsApp, no "how it works"
# ---------------------------------------------------------------------------
def test_admin_sets_footer_contact_email_and_phone(client, db):
    assert "mailto:" not in client.get("/").text  # hidden until set
    admin_login(client, db)
    r = client.post("/admin/home/contact", data={"contact_email": "hello@mina.it", "contact_phone": "01711 111111"})
    assert r.headers["location"] == "/admin/home#contact"
    html = client.get("/products").text
    assert 'href="mailto:hello@mina.it"' in html and 'href="tel:01711111111"' in html
    assert 'value="hello@mina.it"' in client.get("/admin/home").text


def test_contact_settings_missing_table_is_harmless(client, db):
    db.missing_tables.add("site_settings")
    assert client.get("/").status_code == 200


def test_whatsapp_not_named_on_the_bangla_site(client, db):
    db.add("services", title="Repair", slug="repair", price=1000)
    client.cookies.set("lang", "bn")
    for path in ("/", "/services", "/products", "/services/repair"):
        html = client.get(path).text
        assert "হোয়াটসঅ্যাপ" not in html, path
        assert "যেভাবে কাজ করে" not in html and "how-it-works" not in html, path
    assert "অর্ডার করুন" in client.get("/services").text


def test_bangla_text_has_no_letter_spacing(client):
    css = client.get("/static/css/style.css").text
    assert 'html[lang="bn"] .eyebrow' in css and "letter-spacing: normal !important" in css
    client.cookies.set("lang", "bn")
    assert '<html lang="bn"' in client.get("/").text


# ---------------------------------------------------------------------------
# Homepage: products preview, "Why choose us", Schedule a Call
# ---------------------------------------------------------------------------
def test_home_previews_four_products(client, db):
    for i in range(6):
        db.add("products", title=f"Product {i}", slug=f"p{i}", price=100, sort_order=i)
    html = client.get("/").text
    assert "Product 3" in html and "Product 4" not in html
    assert 'href="/products" class="btn-outline"' in html


def test_home_why_choose_us_from_admin(client, db):
    assert 'id="why-us"' not in client.get("/").text  # hidden while empty
    admin_login(client, db)
    client.post("/admin/home/features/new", data={"title": "Same-day support", "title_bn": "একই দিনে সাপোর্ট",
                                                  "description": "Fast.", "sort_order": "1"})
    fid = db.tables["features"][0]["id"]
    assert 'id="why-us"' in client.get("/").text and "Same-day support" in client.get("/").text
    client.cookies.set("lang", "bn")
    assert "একই দিনে সাপোর্ট" in client.get("/").text
    client.post(f"/admin/home/features/{fid}/edit", data={"title": "Quick help"})
    assert db.tables["features"][0]["title"] == "Quick help"
    client.post(f"/admin/home/features/{fid}/delete")
    assert db.tables["features"] == []


def test_admin_home_warns_when_features_table_missing(client, db):
    admin_login(client, db)
    db.missing_tables.add("features")
    assert "run <strong>db/schema.sql</strong> again" in client.get("/admin/home").text
    assert client.get("/").status_code == 200


def test_schedule_a_call_dials_the_phone_when_set(client, db):
    html = client.get("/").text
    assert "https://wa.me/8801700000000?text=" in html  # no phone yet: falls back to chat
    db.add("site_settings", key="contact_phone", value="01711 223344")
    import app.site_settings as site_settings

    site_settings._cache["at"] = 0.0
    assert 'href="tel:01711223344"' in client.get("/").text
