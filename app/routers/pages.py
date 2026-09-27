"""Public, unauthenticated pages: homepage, service detail, blog."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.i18n import LANG_COOKIE, SUPPORTED_LANGS
from app.supabase_client import supabase_admin
from app.templating import base_ctx, templates
from app.utils import render_markdown

router = APIRouter(tags=["pages"])


@router.get("/set-lang/{code}")
def set_lang(code: str, next: str = "/"):
    if code not in SUPPORTED_LANGS:
        code = "en"
    # Only ever redirect back to a path on this same site.
    if not next.startswith("/"):
        next = "/"
    response = RedirectResponse(next, status_code=303)
    response.set_cookie(LANG_COOKIE, code, max_age=60 * 60 * 24 * 365, samesite="lax")
    return response


@router.get("/")
def home(request: Request):
    services = (
        supabase_admin()
        .table("services")
        .select("*")
        .eq("is_active", True)
        .order("sort_order")
        .execute()
        .data
    )
    posts = (
        supabase_admin()
        .table("blog_posts")
        .select("id, title, slug, excerpt, cover_image_url, created_at")
        .eq("is_published", True)
        .order("created_at", desc=True)
        .limit(3)
        .execute()
        .data
    )
    slides = (
        supabase_admin()
        .table("hero_slides")
        .select("*")
        .eq("is_active", True)
        .order("sort_order")
        .execute()
        .data
    )
    stats = (
        supabase_admin().table("site_stats").select("*").order("sort_order").execute().data
    )
    return templates.TemplateResponse(
        "index.html",
        base_ctx(request, services=services, posts=posts, slides=slides, stats=stats),
    )


@router.get("/services/{slug}")
def service_detail(request: Request, slug: str):
    res = (
        supabase_admin()
        .table("services")
        .select("*")
        .eq("slug", slug)
        .eq("is_active", True)
        .maybe_single()
        .execute()
    )
    service = res.data
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return templates.TemplateResponse("service_detail.html", base_ctx(request, service=service))


@router.get("/blog")
def blog_list(request: Request):
    posts = (
        supabase_admin()
        .table("blog_posts")
        .select("id, title, slug, excerpt, cover_image_url, created_at")
        .eq("is_published", True)
        .order("created_at", desc=True)
        .execute()
        .data
    )
    return templates.TemplateResponse("blog_list.html", base_ctx(request, posts=posts))


@router.get("/blog/{slug}")
def blog_post(request: Request, slug: str):
    res = (
        supabase_admin()
        .table("blog_posts")
        .select("*")
        .eq("slug", slug)
        .eq("is_published", True)
        .maybe_single()
        .execute()
    )
    post = res.data
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post["content_html"] = render_markdown(post["content_markdown"])
    return templates.TemplateResponse("blog_post.html", base_ctx(request, post=post))
