"""The "control everything" admin panel: services, orders, blog, customers —
no code edits required to run the business day to day."""
import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse

from app.config import settings
from app.i18n import make_translator
from app.security import CurrentUser, require_admin
from app.supabase_client import fetch_one, supabase_admin
from app.templating import base_ctx, templates
from app.utils import unique_slug, whatsapp_link, whatsapp_number

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
logger = logging.getLogger("minait")

IMAGE_BUCKET = "service-images"
ORDER_STATUSES = ["pending", "in_progress", "completed", "cancelled"]
PAYMENT_STATUSES = ["unpaid", "paid", "failed", "refunded"]


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


def _new_slug(table: str, title: str, fallback: str) -> str:
    """A slug not used by any other row, so two services (or posts) with the
    same title don't crash on the unique constraint."""

    def is_taken(slug: str) -> bool:
        return bool(supabase_admin().table(table).select("id").eq("slug", slug).execute().data)

    return unique_slug(title, fallback, is_taken)


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
    title_bn: str = Form(""),
    description: str = Form(""),
    description_bn: str = Form(""),
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
            "title_bn": title_bn,
            "slug": _new_slug("services", title, "service"),
            "description": description,
            "description_bn": description_bn,
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
    service = fetch_one(supabase_admin().table("services").select("*").eq("id", service_id))
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return templates.TemplateResponse("admin/service_form.html", base_ctx(request, service=service))


@router.post("/services/{service_id}/edit")
async def admin_service_update(
    request: Request,
    service_id: int,
    title: str = Form(...),
    title_bn: str = Form(""),
    description: str = Form(""),
    description_bn: str = Form(""),
    price: float = Form(...),
    currency: str = Form("BDT"),
    category: str = Form("General"),
    icon: str = Form(""),
    image_url: str = Form(""),
    image_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    # The slug is left alone on edit, so links customers already have keep working.
    uploaded_url = await _upload_image(image_file)
    supabase_admin().table("services").update(
        {
            "title": title,
            "title_bn": title_bn,
            "description": description,
            "description_bn": description_bn,
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
    service = fetch_one(supabase_admin().table("services").select("is_active").eq("id", service_id))
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
# Homepage content: hero slider + stat counters.
# However many active slide images / stats exist, that's how many show up on
# the homepage. Slide images carry their own text (designed into the
# picture), so there's nothing to type here — just the picture and its order.
# ---------------------------------------------------------------------------
@router.get("/home")
def admin_home(request: Request):
    slides = supabase_admin().table("hero_slides").select("*").order("sort_order").order("id").execute().data
    stats = supabase_admin().table("site_stats").select("*").order("sort_order").execute().data
    return templates.TemplateResponse(
        "admin/home.html", base_ctx(request, slides=slides, stats=stats)
    )


@router.post("/home/slides/new")
async def admin_slide_create(image_url: str = Form(""), image_file: UploadFile = File(None)):
    uploaded_url = await _upload_image(image_file)
    final_image = uploaded_url or image_url
    if not final_image:
        raise HTTPException(status_code=400, detail="Choose an image to upload — or paste an image URL.")
    next_order = (
        supabase_admin().table("hero_slides").select("id", count="exact").execute().count or 0
    )
    supabase_admin().table("hero_slides").insert(
        {"image_url": final_image, "heading": "", "sort_order": next_order}
    ).execute()
    return RedirectResponse("/admin/home", status_code=303)


@router.post("/home/slides/{slide_id}/toggle")
def admin_slide_toggle(slide_id: int):
    slide = fetch_one(supabase_admin().table("hero_slides").select("is_active").eq("id", slide_id))
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    supabase_admin().table("hero_slides").update({"is_active": not slide["is_active"]}).eq(
        "id", slide_id
    ).execute()
    return RedirectResponse("/admin/home", status_code=303)


@router.post("/home/slides/{slide_id}/delete")
def admin_slide_delete(slide_id: int):
    supabase_admin().table("hero_slides").delete().eq("id", slide_id).execute()
    return RedirectResponse("/admin/home", status_code=303)


@router.post("/home/stats/new")
def admin_stat_create(
    label: str = Form(...), label_bn: str = Form(""), value: str = Form(...), sort_order: int = Form(0)
):
    supabase_admin().table("site_stats").insert(
        {"label": label, "label_bn": label_bn, "value": value, "sort_order": sort_order}
    ).execute()
    return RedirectResponse("/admin/home", status_code=303)


@router.post("/home/stats/{stat_id}/edit")
def admin_stat_update(
    stat_id: int,
    label: str = Form(...),
    label_bn: str = Form(""),
    value: str = Form(...),
    sort_order: int = Form(0),
):
    supabase_admin().table("site_stats").update(
        {"label": label, "label_bn": label_bn, "value": value, "sort_order": sort_order}
    ).eq("id", stat_id).execute()
    return RedirectResponse("/admin/home", status_code=303)


@router.post("/home/stats/{stat_id}/delete")
def admin_stat_delete(stat_id: int):
    supabase_admin().table("site_stats").delete().eq("id", stat_id).execute()
    return RedirectResponse("/admin/home", status_code=303)


# ---------------------------------------------------------------------------
# FAQs: powers the floating "Assistant" widget shown on every page.
# ---------------------------------------------------------------------------
@router.get("/faqs")
def admin_faqs(request: Request):
    faqs = supabase_admin().table("faqs").select("*").order("sort_order").execute().data
    return templates.TemplateResponse("admin/faqs.html", base_ctx(request, faqs=faqs))


@router.post("/faqs/new")
def admin_faq_create(
    question: str = Form(...),
    question_bn: str = Form(""),
    answer: str = Form(...),
    answer_bn: str = Form(""),
    sort_order: int = Form(0),
):
    supabase_admin().table("faqs").insert(
        {
            "question": question,
            "question_bn": question_bn,
            "answer": answer,
            "answer_bn": answer_bn,
            "sort_order": sort_order,
        }
    ).execute()
    return RedirectResponse("/admin/faqs", status_code=303)


@router.post("/faqs/{faq_id}/edit")
def admin_faq_update(
    faq_id: int,
    question: str = Form(...),
    question_bn: str = Form(""),
    answer: str = Form(...),
    answer_bn: str = Form(""),
    sort_order: int = Form(0),
):
    supabase_admin().table("faqs").update(
        {
            "question": question,
            "question_bn": question_bn,
            "answer": answer,
            "answer_bn": answer_bn,
            "sort_order": sort_order,
        }
    ).eq("id", faq_id).execute()
    return RedirectResponse("/admin/faqs", status_code=303)


@router.post("/faqs/{faq_id}/delete")
def admin_faq_delete(faq_id: int):
    supabase_admin().table("faqs").delete().eq("id", faq_id).execute()
    return RedirectResponse("/admin/faqs", status_code=303)


# ---------------------------------------------------------------------------
# Orders tracker
# ---------------------------------------------------------------------------
_en = make_translator("en")
_bn = make_translator("bn")


def customer_update_link(order: dict) -> str | None:
    """WhatsApp link that opens a chat with the customer, pre-filled with the
    order's current status in Bangla and English. This is how customers hear
    about changes — no email is sent. None if there's no usable phone."""
    number = whatsapp_number(order.get("customer_phone"))
    if not number:
        return None
    link = f"{settings.SITE_URL}/orders/{order['order_number']}"
    name = order["customer_name"]
    status, payment = order["status"], order["payment_status"]
    text = (
        f"আসসালামু আলাইকুম {name}, {settings.SITE_NAME} থেকে বলছি। "
        f"আপনার অর্ডার {order['order_number']} ({order['service_title']}) — "
        f"অবস্থা: {_bn('status.' + status)}, পেমেন্ট: {_bn('payment.' + payment)}। "
        f"বিস্তারিত: {link}\n\n"
        f"Hello {name}, your order {order['order_number']} ({order['service_title']}) is now "
        f"{_en('status.' + status)} · Payment: {_en('payment.' + payment)}. Details: {link}"
    )
    return whatsapp_link(number, text)


def _orders_url(status_filter: str) -> str:
    return f"/admin/orders?status={status_filter}" if status_filter in ORDER_STATUSES else "/admin/orders"


@router.get("/orders")
def admin_orders(request: Request, status: str | None = None):
    query = supabase_admin().table("orders").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    orders = query.execute().data
    for o in orders:
        o["wa_link"] = customer_update_link(o)
    return templates.TemplateResponse(
        "admin/orders.html",
        base_ctx(
            request,
            orders=orders,
            active_status=status,
            order_statuses=ORDER_STATUSES,
            payment_statuses=PAYMENT_STATUSES,
        ),
    )


@router.post("/orders/{order_id}/status")
def admin_order_update_status(
    order_id: int,
    status: str = Form(...),
    payment_status: str = Form(""),
    back: str = Form(""),
):
    """Saves the work status and (when sent) the payment status together —
    e.g. marking a WhatsApp/cash order as paid, which no gateway will ever
    do automatically."""
    if status not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Unknown order status")
    changes = {"status": status}
    if payment_status:
        if payment_status not in PAYMENT_STATUSES:
            raise HTTPException(status_code=400, detail="Unknown payment status")
        changes["payment_status"] = payment_status
    supabase_admin().table("orders").update(changes).eq("id", order_id).execute()
    return RedirectResponse(f"{_orders_url(back)}#order-{order_id}", status_code=303)


# ---------------------------------------------------------------------------
# Customers: see who signed up, and set a new password for someone who
# forgot theirs (there's no reset email — see auth.py).
# ---------------------------------------------------------------------------
def _users_page(request: Request, **extra):
    profiles = {p["id"]: p for p in supabase_admin().table("profiles").select("*").execute().data}
    users = []
    for u in supabase_admin().auth.admin.list_users(page=1, per_page=1000):
        p = profiles.get(u.id, {})
        users.append(
            {
                "id": u.id,
                "email": u.email or "",
                "full_name": p.get("full_name") or "",
                "phone": p.get("phone") or "",
                "is_admin": bool(p.get("is_admin")),
                "created_at": str(u.created_at or "")[:10],
            }
        )
    users.sort(key=lambda u: u["created_at"], reverse=True)
    return templates.TemplateResponse("admin/users.html", base_ctx(request, users=users, **extra))


@router.get("/users")
def admin_users(request: Request):
    return _users_page(request)


@router.post("/users/{user_id}/password")
def admin_user_set_password(request: Request, user_id: str, new_password: str = Form(...)):
    if len(new_password) < 6:
        return _users_page(request, error="Password must be at least 6 characters.")
    try:
        supabase_admin().auth.admin.update_user_by_id(user_id, {"password": new_password})
    except Exception:
        logger.exception("Admin password reset failed for user %s", user_id)
        return _users_page(request, error="Couldn't set the password — please try again.")

    profile = fetch_one(supabase_admin().table("profiles").select("*").eq("id", user_id)) or {}
    number = whatsapp_number(profile.get("phone"))
    wa = None
    if number:
        wa = whatsapp_link(
            number,
            f"আপনার {settings.SITE_NAME} অ্যাকাউন্টের নতুন পাসওয়ার্ড: {new_password}\n"
            f"লগ ইন করে ড্যাশবোর্ড থেকে পাসওয়ার্ডটি বদলে নিন: {settings.SITE_URL}/login\n\n"
            f"Your new {settings.SITE_NAME} password: {new_password}\n"
            f"Please log in and change it from your dashboard.",
        )
    return _users_page(request, message="Password updated.", reset_user_id=user_id, reset_wa_link=wa)


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
    title_bn: str = Form(""),
    excerpt: str = Form(""),
    excerpt_bn: str = Form(""),
    content_markdown: str = Form(...),
    content_markdown_bn: str = Form(""),
    cover_image_url: str = Form(""),
    cover_image_file: UploadFile = File(None),
    is_published: bool = Form(False),
):
    uploaded_url = await _upload_image(cover_image_file)
    supabase_admin().table("blog_posts").insert(
        {
            "title": title,
            "title_bn": title_bn,
            "slug": _new_slug("blog_posts", title, "post"),
            "excerpt": excerpt,
            "excerpt_bn": excerpt_bn,
            "content_markdown": content_markdown,
            "content_markdown_bn": content_markdown_bn,
            "cover_image_url": uploaded_url or cover_image_url,
            "is_published": is_published,
            "author_id": user.id,
        }
    ).execute()
    return RedirectResponse("/admin/blog", status_code=303)


@router.get("/blog/{post_id}/edit")
def admin_blog_edit_page(request: Request, post_id: int):
    post = fetch_one(supabase_admin().table("blog_posts").select("*").eq("id", post_id))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("admin/blog_form.html", base_ctx(request, post=post))


@router.post("/blog/{post_id}/edit")
async def admin_blog_update(
    request: Request,
    post_id: int,
    title: str = Form(...),
    title_bn: str = Form(""),
    excerpt: str = Form(""),
    excerpt_bn: str = Form(""),
    content_markdown: str = Form(...),
    content_markdown_bn: str = Form(""),
    cover_image_url: str = Form(""),
    cover_image_file: UploadFile = File(None),
    is_published: bool = Form(False),
):
    uploaded_url = await _upload_image(cover_image_file)
    supabase_admin().table("blog_posts").update(
        {
            "title": title,
            "title_bn": title_bn,
            "excerpt": excerpt,
            "excerpt_bn": excerpt_bn,
            "content_markdown": content_markdown,
            "content_markdown_bn": content_markdown_bn,
            "cover_image_url": uploaded_url or cover_image_url,
            "is_published": is_published,
        }
    ).eq("id", post_id).execute()
    return RedirectResponse("/admin/blog", status_code=303)


@router.post("/blog/{post_id}/feature")
def admin_blog_feature(post_id: int):
    """Makes this post the big "top post" on /blog (only one at a time), or
    un-picks it if it already is — then the newest post goes on top."""
    post = fetch_one(supabase_admin().table("blog_posts").select("*").eq("id", post_id))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    supabase_admin().table("blog_posts").update({"is_featured": False}).eq("is_featured", True).execute()
    if not post.get("is_featured"):
        supabase_admin().table("blog_posts").update({"is_featured": True}).eq("id", post_id).execute()
    return RedirectResponse("/admin/blog", status_code=303)


@router.post("/blog/{post_id}/delete")
def admin_blog_delete(post_id: int):
    supabase_admin().table("blog_posts").delete().eq("id", post_id).execute()
    return RedirectResponse("/admin/blog", status_code=303)
