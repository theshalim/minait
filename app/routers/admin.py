"""The "control everything" admin panel: services, orders, blog — no code
edits required to run the business day to day."""
import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse

from app.security import CurrentUser, require_admin
from app.supabase_client import supabase_admin
from app.templating import base_ctx, templates
from app.utils import slugify

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
logger = logging.getLogger("minait")

IMAGE_BUCKET = "service-images"


async def _upload_image(file: UploadFile | None) -> str | None:
    """Uploads a submitted file to Supabase Storage and returns its public
    URL, or None if nothing was uploaded (or the upload failed — in which
    case the caller falls back to the manually-typed image URL field
    instead of blowing up the whole form submission)."""
    if not file or not file.filename:
        return None
    try:
        data = await file.read()
        if not data:
            return None
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
        path = f"{uuid.uuid4().hex}.{ext}"
        supabase_admin().storage.from_(IMAGE_BUCKET).upload(
            path, data, {"content-type": file.content_type or "image/jpeg"}
        )
        return supabase_admin().storage.from_(IMAGE_BUCKET).get_public_url(path)
    except Exception:
        logger.exception("Image upload failed")
        return None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@router.get("")
def admin_dashboard(request: Request, user: CurrentUser = Depends(require_admin)):
    orders = supabase_admin().table("orders").select("*").order("created_at", desc=True).execute().data
    services = supabase_admin().table("services").select("id", count="exact").execute()
    posts = supabase_admin().table("blog_posts").select("id", count="exact").execute()

    stats = {
        "total_orders": len(orders),
        "pending_orders": sum(1 for o in orders if o["status"] == "pending"),
        "revenue": sum(float(o["amount"]) for o in orders if o["payment_status"] == "paid"),
        "total_services": services.count or 0,
        "total_posts": posts.count or 0,
    }
    return templates.TemplateResponse(
        "admin/dashboard.html", base_ctx(request, stats=stats, recent_orders=orders[:8])
    )


# ---------------------------------------------------------------------------
# Services CRUD
# ---------------------------------------------------------------------------
@router.get("/services")
def admin_services(request: Request):
    services = supabase_admin().table("services").select("*").order("sort_order").execute().data
    return templates.TemplateResponse("admin/services.html", base_ctx(request, services=services, service=None))


@router.get("/services/new")
def admin_service_new(request: Request):
    return templates.TemplateResponse("admin/service_form.html", base_ctx(request, service=None))


@router.post("/services/new")
async def admin_service_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    currency: str = Form("BDT"),
    category: str = Form("General"),
    icon: str = Form(""),
    image_url: str = Form(""),
    image_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    uploaded_url = await _upload_image(image_file)
    supabase_admin().table("services").insert(
        {
            "title": title,
            "slug": slugify(title),
            "description": description,
            "price": price,
            "currency": currency,
            "category": category,
            "icon": icon,
            "image_url": uploaded_url or image_url,
            "sort_order": sort_order,
        }
    ).execute()
    return RedirectResponse("/admin/services", status_code=303)


@router.get("/services/{service_id}/edit")
def admin_service_edit_page(request: Request, service_id: int):
    service = supabase_admin().table("services").select("*").eq("id", service_id).maybe_single().execute().data
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return templates.TemplateResponse("admin/service_form.html", base_ctx(request, service=service))


@router.post("/services/{service_id}/edit")
async def admin_service_update(
    request: Request,
    service_id: int,
    title: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    currency: str = Form("BDT"),
    category: str = Form("General"),
    icon: str = Form(""),
    image_url: str = Form(""),
    image_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    uploaded_url = await _upload_image(image_file)
    supabase_admin().table("services").update(
        {
            "title": title,
            "description": description,
            "price": price,
            "currency": currency,
            "category": category,
            "icon": icon,
            "image_url": uploaded_url or image_url,
            "sort_order": sort_order,
        }
    ).eq("id", service_id).execute()
    return RedirectResponse("/admin/services", status_code=303)


@router.post("/services/{service_id}/toggle")
def admin_service_toggle(service_id: int):
    service = supabase_admin().table("services").select("is_active").eq("id", service_id).maybe_single().execute().data
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    supabase_admin().table("services").update({"is_active": not service["is_active"]}).eq(
        "id", service_id
    ).execute()
    return RedirectResponse("/admin/services", status_code=303)


@router.post("/services/{service_id}/delete")
def admin_service_delete(service_id: int):
    supabase_admin().table("services").delete().eq("id", service_id).execute()
    return RedirectResponse("/admin/services", status_code=303)


# ---------------------------------------------------------------------------
# Orders tracker
# ---------------------------------------------------------------------------
@router.get("/orders")
def admin_orders(request: Request, status: str | None = None):
    query = supabase_admin().table("orders").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    orders = query.execute().data
    return templates.TemplateResponse(
        "admin/orders.html", base_ctx(request, orders=orders, active_status=status)
    )


@router.post("/orders/{order_id}/status")
def admin_order_update_status(order_id: int, status: str = Form(...)):
    supabase_admin().table("orders").update({"status": status}).eq("id", order_id).execute()
    return RedirectResponse("/admin/orders", status_code=303)


# ---------------------------------------------------------------------------
# Blog manager
# ---------------------------------------------------------------------------
@router.get("/blog")
def admin_blog(request: Request):
    posts = supabase_admin().table("blog_posts").select("*").order("created_at", desc=True).execute().data
    return templates.TemplateResponse("admin/blog.html", base_ctx(request, posts=posts))


@router.get("/blog/new")
def admin_blog_new(request: Request):
    return templates.TemplateResponse("admin/blog_form.html", base_ctx(request, post=None))


@router.post("/blog/new")
async def admin_blog_create(
    request: Request,
    user: CurrentUser = Depends(require_admin),
    title: str = Form(...),
    excerpt: str = Form(""),
    content_markdown: str = Form(...),
    cover_image_url: str = Form(""),
    cover_image_file: UploadFile = File(None),
    is_published: bool = Form(False),
):
    uploaded_url = await _upload_image(cover_image_file)
    supabase_admin().table("blog_posts").insert(
        {
            "title": title,
            "slug": slugify(title),
            "excerpt": excerpt,
            "content_markdown": content_markdown,
            "cover_image_url": uploaded_url or cover_image_url,
            "is_published": is_published,
            "author_id": user.id,
        }
    ).execute()
    return RedirectResponse("/admin/blog", status_code=303)


@router.get("/blog/{post_id}/edit")
def admin_blog_edit_page(request: Request, post_id: int):
    post = supabase_admin().table("blog_posts").select("*").eq("id", post_id).maybe_single().execute().data
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("admin/blog_form.html", base_ctx(request, post=post))


@router.post("/blog/{post_id}/edit")
async def admin_blog_update(
    request: Request,
    post_id: int,
    title: str = Form(...),
    excerpt: str = Form(""),
    content_markdown: str = Form(...),
    cover_image_url: str = Form(""),
    cover_image_file: UploadFile = File(None),
    is_published: bool = Form(False),
):
    uploaded_url = await _upload_image(cover_image_file)
    supabase_admin().table("blog_posts").update(
        {
            "title": title,
            "excerpt": excerpt,
            "content_markdown": content_markdown,
            "cover_image_url": uploaded_url or cover_image_url,
            "is_published": is_published,
        }
    ).eq("id", post_id).execute()
    return RedirectResponse("/admin/blog", status_code=303)


@router.post("/blog/{post_id}/delete")
def admin_blog_delete(post_id: int):
    supabase_admin().table("blog_posts").delete().eq("id", post_id).execute()
    return RedirectResponse("/admin/blog", status_code=303)
