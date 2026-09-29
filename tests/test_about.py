"""About us page, its admin editor, and the "Our Service Basket" SQL."""
import pglast

from tests.test_app import admin_login


def test_about_page_with_defaults(client, db):
    html = client.get("/about").text
    assert "Mina IT: We make" in html and '<span class="text-gradient">technology simple</span>' in html
    assert 'href="/about"' in html  # in the navbar
    assert 'id="contact"' in html


def test_about_page_uses_why_points_and_counters(client, db):
    db.add("features", title="Same-day support", description="Fast.")
    db.add("site_stats", label="Happy clients", value="20+")
    html = client.get("/about").text
    assert "Same-day support" in html and "20+" in html and "Happy clients" in html


def test_about_page_bangla_defaults(client, db):
    client.cookies.set("lang", "bn")
    html = client.get("/about").text
    assert "মিনা আইটি" in html and '<span class="text-gradient">প্রযুক্তি সহজ</span>' in html


def test_admin_edits_about_texts(client, db):
    admin_login(client, db)
    page = client.get("/admin/about").text
    assert 'name="about_hero_title"' in page and 'name="about_hero_title_bn"' in page
    r = client.post("/admin/about", data={"about_hero_title": "We are *Mina*", "about_story_text": "Our story.",
                                          "about_cta_heading_bn": "চলুন *কথা বলি*", "story_url": "https://img/team.jpg"})
    assert r.headers["location"] == "/admin/about?saved=1"
    html = client.get("/about").text
    assert 'We are <span class="text-gradient">Mina</span>' in html and "Our story." in html
    assert 'src="https://img/team.jpg"' in html
    client.cookies.set("lang", "bn")
    bn = client.get("/about").text
    assert 'চলুন <span class="text-gradient">কথা বলি</span>' in bn
    assert "Our story." in bn  # admin's own English beats the generic Bangla default


def test_about_highlight_escapes_html(client, db):
    admin_login(client, db)
    client.post("/admin/about", data={"about_hero_title": "<script>x</script> *hi*"})
    html = client.get("/about").text
    assert "<script>x</script>" not in html and "&lt;script&gt;" in html


def test_service_basket_sql():
    stmts = pglast.parse_sql(open("db/service_basket.sql", encoding="utf8").read())
    insert = [s.stmt for s in stmts if type(s.stmt).__name__ == "InsertStmt"][0]
    rows = insert.selectStmt.fromClause[0].subquery.valuesLists
    titles = [r[0].val.sval for r in rows]
    assert titles == ["Custom Software Development", "Web Development & Maintenance",
                      "Cloud Management", "IT Infrastructure"]
    for r in rows:
        assert r[3].val.sval == "Our Service Basket" and r[4].val.sval == "আমাদের সার্ভিস বাস্কেট"
        assert "Bangladesh" in open("db/service_basket.sql", encoding="utf8").read()
        assert r[10].val.sval.startswith("https://images.unsplash.com/")


def test_service_detail_category_in_bangla(client, db):
    db.add("services", title="Cloud", slug="cloud", price=0, category="Our Service Basket",
           category_bn="আমাদের সার্ভিস বাস্কেট")
    client.cookies.set("lang", "bn")
    html = client.get("/services/cloud").text
    assert "আমাদের সার্ভিস বাস্কেট" in html and "Our Service Basket" not in html
