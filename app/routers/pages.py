"""Public, unauthenticated pages: homepage, services, products, blog."""
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.i18n import LANG_COOKIE, SUPPORTED_LANGS, get_locale, localized, make_translator
from app.supabase_client import fetch_one, supabase_admin
from app.templating import base_ctx, templates
from app.utils import render_markdown

router = APIRouter(tags=["pages"])
logger = logging.getLogger("minait")


@router.get("/set-lang/{code}")
def set_lang(code: str, next: str = "/"):
    if code not in SUPPORTED_LANGS:
        code = "en"
    # Only ever redirect back to a path on this same site.
    if not next.startswith("/") or next.startswith("//"):
        next = "/"
    response = RedirectResponse(next, status_code=303)
    response.set_cookie(LANG_COOKIE, code, max_age=60 * 60 * 24 * 365, samesite="lax")
    return response


# Public pages select "*" so the optional Bangla (`*_bn`) columns come along
# whenever they exist, without breaking if the database hasn't got them yet.
def _active(table: str) -> list[dict]:
    return (
        supabase_admin().table(table).select("*").eq("is_active", True).order("sort_order").execute().data
    )


def _optional(fetch) -> list[dict]:
    """For sections backed by newer tables (products, testimonials, client
    logos): if db/schema.sql hasn't been re-run yet and the table is
    missing, show the page without that section instead of an error."""
    try:
        return fetch()
    except Exception:
        logger.exception("Optional section failed to load")
        return []


@router.get("/")
def home(request: Request):
    posts = (
        supabase_admin()
        .table("blog_posts")
        .select("*")
        .eq("is_published", True)
        .order("created_at", desc=True)
        .limit(3)
        .execute()
        .data
    )
    stats = (
        supabase_admin().table("site_stats").select("*").order("sort_order").execute().data
    )
    return templates.TemplateResponse(
        "index.html",
        base_ctx(
            request,
            services=_active("services"),
            posts=posts,
            slides=_active("hero_slides"),
            stats=stats,
            products=_optional(lambda: _active("products")),
            features=_optional(
                lambda: supabase_admin().table("features").select("*").order("sort_order").execute().data
            ),
            testimonials=_optional(lambda: _active("testimonials")),
            clients=_optional(
                lambda: supabase_admin().table("clients").select("*").order("sort_order").execute().data
            ),
        ),
    )


@router.get("/services")
def services_page(request: Request):
    t = make_translator(get_locale(request))
    return templates.TemplateResponse(
        "services.html",
        base_ctx(
            request, items=_active("services"), kind="service",
            heading=t("services.heading"), intro=t("services.intro"), empty=t("home.no_services"),
        ),
    )


@router.get("/products")
def products_page(request: Request):
    t = make_translator(get_locale(request))
    return templates.TemplateResponse(
        "services.html",
        base_ctx(
            request, items=_optional(lambda: _active("products")), kind="product",
            heading=t("products.heading"), intro=t("products.intro"), empty=t("products.empty"),
        ),
    )


@router.get("/api/faqs")
def api_faqs(request: Request):
    """Public, read-only. Powers the floating Assistant widget's FAQ list —
    fetched lazily by main.js the first time someone opens it, rather than
    on every page load. Answers come in the visitor's language."""
    lang = get_locale(request)
    faqs = supabase_admin().table("faqs").select("*").order("sort_order").execute().data
    return [
        {"question": localized(f, "question", lang), "answer": localized(f, "answer", lang)}
        for f in faqs
    ]


@router.get("/services/{slug}")
def service_detail(request: Request, slug: str):
    service = fetch_one(
        supabase_admin().table("services").select("*").eq("slug", slug).eq("is_active", True)
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return templates.TemplateResponse("service_detail.html", base_ctx(request, service=service))


BLOG_PAGE_SIZE = 10


@router.get("/blog")
def blog_list(request: Request, q: str = "", page: int = 1):
    """Blog index: one big "top post" (the one the admin picked, else the
    newest) above a paged list of the rest. Searching shows plain results."""
    posts = (
        supabase_admin()
        .table("blog_posts")
        .select("*")
        .eq("is_published", True)
        .order("created_at", desc=True)
        .execute()
        .data
    )
    q = q.strip()
    featured = None
    if q:
        needle = q.lower()
        fields = ("title", "title_bn", "excerpt", "excerpt_bn")
        posts = [p for p in posts if any(needle in (p.get(f) or "").lower() for f in fields)]
    elif posts:
        featured = next((p for p in posts if p.get("is_featured")), posts[0])
        posts = [p for p in posts if p is not featured]

    pages = max(1, -(-len(posts) // BLOG_PAGE_SIZE))
    page = min(max(page, 1), pages)
    start = (page - 1) * BLOG_PAGE_SIZE
    return templates.TemplateResponse(
        "blog_list.html",
        base_ctx(
            request,
            featured=featured if page == 1 else None,
            posts=posts[start : start + BLOG_PAGE_SIZE],
            q=q,
            page=page,
            pages=pages,
        ),
    )


@router.get("/blog/{slug}")
def blog_post(request: Request, slug: str):
    post = fetch_one(
        supabase_admin().table("blog_posts").select("*").eq("slug", slug).eq("is_published", True)
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post["content_html"] = render_markdown(localized(post, "content_markdown", get_locale(request)))
    return templates.TemplateResponse("blog_post.html", base_ctx(request, post=post))
