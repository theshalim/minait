"""The website's "Order now" / "Book a demo" form.

Visitors don't need WhatsApp (or an account): they leave their name, an
email or phone, and what they need. Each request is saved as an order
(Admin -> Orders, marked "Demo request" for demos) and the admin gets a
Telegram/Discord alert. The page also lists call / email / chat for anyone
who'd rather talk directly.
"""
import logging

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.i18n import get_locale, localized, make_translator
from app.notify import notify_new_request
from app.supabase_client import fetch_one, supabase_admin
from app.templating import base_ctx, templates
from app.utils import generate_order_number

router = APIRouter(tags=["enquiry"])
logger = logging.getLogger("minait")

TABLES = {"service": "services", "product": "products"}


def _item(kind: str, slug: str) -> dict:
    table = TABLES.get(kind)
    item = fetch_one(supabase_admin().table(table).select("*").eq("slug", slug).eq("is_active", True)) if table else None
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


def _form_page(request: Request, kind: str, item: dict, request_type: str, **extra):
    t = make_translator(get_locale(request))
    title_key = "enquiry.demo_title" if request_type == "demo" else "enquiry.order_title"
    return templates.TemplateResponse(
        "enquiry.html",
        base_ctx(
            request,
            kind=kind,
            item=item,
            request_type=request_type,
            heading=t(title_key, title=localized(item, "title", get_locale(request))),
            form=extra.pop("form", {}),
            **extra,
        ),
    )


@router.get("/order/{kind}/{slug}")
def enquiry_page(request: Request, kind: str, slug: str, type: str = "order"):
    return _form_page(request, kind, _item(kind, slug), "demo" if type == "demo" else "order")


@router.post("/order/{kind}/{slug}")
def enquiry_submit(
    request: Request,
    kind: str,
    slug: str,
    request_type: str = Form("order"),
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    company: str = Form(""),
    message: str = Form(""),
    preferred_time: str = Form(""),
    website: str = Form(""),  # honeypot: real people never see or fill this
):
    item = _item(kind, slug)
    request_type = "demo" if request_type == "demo" else "order"
    form = {"name": name, "email": email, "phone": phone, "company": company,
            "message": message, "preferred_time": preferred_time}
    if website:
        return RedirectResponse("/", status_code=303)  # a bot — pretend it worked
    if not email.strip() and not phone.strip():
        t = make_translator(get_locale(request))
        return _form_page(request, kind, item, request_type, form=form, error=t("enquiry.need_contact"))

    notes = "\n".join(
        line for line in (
            message.strip(),
            f"Company: {company.strip()}" if company.strip() else "",
            f"Preferred time: {preferred_time.strip()}" if preferred_time.strip() else "",
        ) if line
    )
    order = {
        "order_number": generate_order_number(),
        "service_id": item["id"] if kind == "service" else None,
        "service_title": ("Demo — " if request_type == "demo" else "") + item["title"],
        "customer_name": name.strip(),
        "customer_email": email.strip(),
        "customer_phone": phone.strip(),
        "notes": notes,
        "amount": 0,
        "currency": "BDT",
        "payment_method": "form",
        "payment_status": "unpaid",
        "status": "pending",
        "kind": request_type,
    }
    try:
        created = supabase_admin().table("orders").insert(order).execute().data[0]
    except Exception:
        # The `kind` column only exists once db/schema.sql has been re-run.
        logger.exception("Order insert with kind failed; retrying without it")
        order.pop("kind")
        created = supabase_admin().table("orders").insert(order).execute().data[0]
    notify_new_request({**created, "kind": request_type})
    return RedirectResponse(f"/thank-you/{created['order_number']}", status_code=303)


@router.get("/thank-you/{order_number}")
def enquiry_thanks(request: Request, order_number: str):
    order = fetch_one(supabase_admin().table("orders").select("*").eq("order_number", order_number))
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse("enquiry_thanks.html", base_ctx(request, order=order))
