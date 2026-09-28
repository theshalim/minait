"""The "control everything" admin panel: services, products, orders, blog,
homepage content, clients and the admin's own account — no code edits
required to run the business day to day."""
import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse

from app.config import settings
from app.i18n import make_translator
from app.security import CurrentUser, check_password, require_admin
from app.supabase_client import fetch_one, supabase_admin
from app.templating import base_ctx, templates
from app.utils import generate_order_number, unique_slug, whatsapp_link, whatsapp_number

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


def _catalog_titles() -> list[str]:
    """Service + product names, offered as suggestions in "Add order"."""
    titles = [s["title"] for s in supabase_admin().table("services").select("title").order("sort_order").execute().data]
    try:
        titles += [p["title"] for p in supabase_admin().table("products").select("title").order("sort_order").execute().data]
    except Exception:
        pass  # products table not created yet
    return titles


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
            catalog_titles=_catalog_titles(),
        ),
    )


@router.post("/orders/new")
def admin_order_create(
    customer_name: str = Form(...),
    customer_phone: str = Form(""),
    customer_email: str = Form(""),
    service_title: str = Form(...),
    amount: float = Form(0),
    currency: str = Form("BDT"),
    notes: str = Form(""),
    status: str = Form("pending"),
    payment_status: str = Form("unpaid"),
):
    """Logs an order that came in over WhatsApp chat, so it shows up in the
    tracker, the revenue total and gets a tracking link for the customer."""
    if status not in ORDER_STATUSES or payment_status not in PAYMENT_STATUSES:
        raise HTTPException(status_code=400, detail="Unknown status")
    created = supabase_admin().table("orders").insert(
        {
            "order_number": generate_order_number(),
            "service_title": service_title.strip(),
            "customer_name": customer_name.strip(),
            "customer_email": customer_email.strip(),
            "customer_phone": customer_phone.strip(),
            "notes": notes,
            "amount": amount,
            "currency": currency or "BDT",
            "payment_method": "whatsapp",
            "payment_status": payment_status,
            "status": status,
        }
    ).execute().data[0]
    return RedirectResponse(f"/admin/orders#order-{created['id']}", status_code=303)


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


@router.post("/orders/{order_id}/delete")
def admin_order_delete(order_id: int):
    supabase_admin().table("orders").delete().eq("id", order_id).execute()
    return RedirectResponse("/admin/orders", status_code=303)


# ---------------------------------------------------------------------------
# Account: the admin changes their own password. (A forgotten password is
# reset from the Supabase dashboard — the site sends no email.)
# ---------------------------------------------------------------------------
@router.get("/account")
def admin_account(request: Request):
    return templates.TemplateResponse("admin/account.html", base_ctx(request))


@router.post("/account/password")
def admin_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: CurrentUser = Depends(require_admin),
):
    def page(**msg):
        return templates.TemplateResponse("admin/account.html", base_ctx(request, **msg))

    if len(new_password) < 8:
        return page(error="The new password must be at least 8 characters.")
    if new_password != confirm_password:
        return page(error="The two new passwords don't match.")
    try:
        if not check_password(user.email, current_password):
            return page(error="Your current password is wrong.")
        supabase_admin().auth.admin.update_user_by_id(user.id, {"password": new_password})
    except Exception:
        logger.exception("Admin password change failed")
        return page(error="Couldn't change the password right now — please try again.")
    return page(message="Password changed. Use the new one next time you log in.")


# ---------------------------------------------------------------------------
# Products CRUD (same shape as services; price is optional)
# ---------------------------------------------------------------------------
def _product_fields(title, title_bn, description, description_bn, price, currency, category, image):
    return {
        "title": title,
        "title_bn": title_bn,
        "description": description,
        "description_bn": description_bn,
        "price": float(price) if str(price).strip() else None,
        "currency": currency or "BDT",
        "category": category,
        "image_url": image,
    }


@router.get("/products")
def admin_products(request: Request):
    products = supabase_admin().table("products").select("*").order("sort_order").execute().data
    return templates.TemplateResponse("admin/products.html", base_ctx(request, products=products))


@router.get("/products/new")
def admin_product_new(request: Request):
    return templates.TemplateResponse("admin/product_form.html", base_ctx(request, product=None))


@router.post("/products/new")
async def admin_product_create(
    title: str = Form(...),
    title_bn: str = Form(""),
    description: str = Form(""),
    description_bn: str = Form(""),
    price: str = Form(""),
    currency: str = Form("BDT"),
    category: str = Form(""),
    image_url: str = Form(""),
    image_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    uploaded_url = await _upload_image(image_file)
    row = _product_fields(title, title_bn, description, description_bn, price, currency, category,
                          uploaded_url or image_url)
    row.update(slug=_new_slug("products", title, "product"), sort_order=sort_order)
    supabase_admin().table("products").insert(row).execute()
    return RedirectResponse("/admin/products", status_code=303)


@router.get("/products/{product_id}/edit")
def admin_product_edit_page(request: Request, product_id: int):
    product = fetch_one(supabase_admin().table("products").select("*").eq("id", product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return templates.TemplateResponse("admin/product_form.html", base_ctx(request, product=product))


@router.post("/products/{product_id}/edit")
async def admin_product_update(
    product_id: int,
    title: str = Form(...),
    title_bn: str = Form(""),
    description: str = Form(""),
    description_bn: str = Form(""),
    price: str = Form(""),
    currency: str = Form("BDT"),
    category: str = Form(""),
    image_url: str = Form(""),
    image_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    uploaded_url = await _upload_image(image_file)
    row = _product_fields(title, title_bn, description, description_bn, price, currency, category,
                          uploaded_url or image_url)
    row["sort_order"] = sort_order
    supabase_admin().table("products").update(row).eq("id", product_id).execute()
    return RedirectResponse("/admin/products", status_code=303)


@router.post("/products/{product_id}/toggle")
def admin_product_toggle(product_id: int):
    product = fetch_one(supabase_admin().table("products").select("is_active").eq("id", product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    supabase_admin().table("products").update({"is_active": not product["is_active"]}).eq(
        "id", product_id
    ).execute()
    return RedirectResponse("/admin/products", status_code=303)


@router.post("/products/{product_id}/delete")
def admin_product_delete(product_id: int):
    supabase_admin().table("products").delete().eq("id", product_id).execute()
    return RedirectResponse("/admin/products", status_code=303)


# ---------------------------------------------------------------------------
# Clients: "What our clients say" testimonials + the moving "Trusted by"
# logo strip, both on the homepage.
# ---------------------------------------------------------------------------
@router.get("/clients")
def admin_clients(request: Request):
    testimonials = supabase_admin().table("testimonials").select("*").order("sort_order").execute().data
    clients = supabase_admin().table("clients").select("*").order("sort_order").execute().data
    return templates.TemplateResponse(
        "admin/clients.html", base_ctx(request, testimonials=testimonials, clients=clients)
    )


@router.post("/clients/testimonials/new")
async def admin_testimonial_create(
    name: str = Form(...),
    role: str = Form(""),
    role_bn: str = Form(""),
    message: str = Form(...),
    message_bn: str = Form(""),
    image_url: str = Form(""),
    image_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    uploaded_url = await _upload_image(image_file)
    supabase_admin().table("testimonials").insert(
        {"name": name, "role": role, "role_bn": role_bn, "message": message, "message_bn": message_bn,
         "image_url": uploaded_url or image_url, "sort_order": sort_order}
    ).execute()
    return RedirectResponse("/admin/clients", status_code=303)


@router.post("/clients/testimonials/{tid}/edit")
async def admin_testimonial_update(
    tid: int,
    name: str = Form(...),
    role: str = Form(""),
    role_bn: str = Form(""),
    message: str = Form(...),
    message_bn: str = Form(""),
    image_url: str = Form(""),
    image_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    uploaded_url = await _upload_image(image_file)
    supabase_admin().table("testimonials").update(
        {"name": name, "role": role, "role_bn": role_bn, "message": message, "message_bn": message_bn,
         "image_url": uploaded_url or image_url, "sort_order": sort_order}
    ).eq("id", tid).execute()
    return RedirectResponse(f"/admin/clients#testimonial-{tid}", status_code=303)


@router.post("/clients/testimonials/{tid}/toggle")
def admin_testimonial_toggle(tid: int):
    row = fetch_one(supabase_admin().table("testimonials").select("is_active").eq("id", tid))
    if not row:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    supabase_admin().table("testimonials").update({"is_active": not row["is_active"]}).eq("id", tid).execute()
    return RedirectResponse(f"/admin/clients#testimonial-{tid}", status_code=303)


@router.post("/clients/testimonials/{tid}/delete")
def admin_testimonial_delete(tid: int):
    supabase_admin().table("testimonials").delete().eq("id", tid).execute()
    return RedirectResponse("/admin/clients", status_code=303)


@router.post("/clients/logos/new")
async def admin_client_logo_create(
    name: str = Form(...),
    website_url: str = Form(""),
    logo_url: str = Form(""),
    logo_file: UploadFile = File(None),
    sort_order: int = Form(0),
):
    uploaded_url = await _upload_image(logo_file)
    supabase_admin().table("clients").insert(
        {"name": name, "website_url": website_url, "logo_url": uploaded_url or logo_url, "sort_order": sort_order}
    ).execute()
    return RedirectResponse("/admin/clients#logos", status_code=303)


@router.post("/clients/logos/{cid}/delete")
def admin_client_logo_delete(cid: int):
    supabase_admin().table("clients").delete().eq("id", cid).execute()
    return RedirectResponse("/admin/clients#logos", status_code=303)


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
