"""Minimal English/Bangla translation layer.

No framework, just a dict lookup — enough for a small marketing +
storefront site. The locale is remembered in a plain (non-httponly, so
JS could read it too if ever needed) cookie set by GET /set-lang/{code}.

Admin pages are intentionally left in English only (internal tool for
the business owner), so only the public-facing / customer templates
pull their strings through t().
"""
from fastapi import Request

LANG_COOKIE = "lang"
DEFAULT_LANG = "en"
SUPPORTED_LANGS = ("en", "bn")

TRANSLATIONS = {
    "en": {
        "nav.services": "Services",
        "nav.blog": "Blog",
        "footer.tagline": "Straightforward IT services for home and business.",
        "footer.explore": "Explore",
        "footer.talk_to_us": "Talk to us",
        "footer.rights": "All rights reserved.",
        "home.badge": "Trusted IT services, delivered fast",
        "home.title": "Get expert IT help without the runaround.",
        "home.subtitle": "Pick a service and send us a message. We'll take it from there.",
        "home.browse_services": "Browse services",
        "home.chat_with_us": "Chat with us",
        "home.schedule_call": "Schedule a Call",
        "home.services_heading": "Our Services",
        "home.no_services": "Services are coming soon — check back shortly.",
        "home.blog_heading": "From the blog",
        "home.view_all": "View all →",
        "login.title": "Admin sign in",
        "login.email": "Email",
        "login.password": "Password",
        "login.submit": "Log in",
        "service.order_now": "Order Now",
        "service.price": "Price",
        "service.back": "← All services",
        "blog.heading": "Mina IT Blog",
        "blog.empty": "No articles yet — check back soon.",
        "blog.back": "← All articles",
        "blog.learn_more": "Learn more",
        "blog.search": "Search blog",
        "blog.no_results": "No articles match your search.",
        "blog.previous": "Previous",
        "blog.next": "Next",
        "blog.share_facebook": "Share on Facebook",
        "blog.share_x": "Share on X",
        "blog.share_linkedin": "Share on LinkedIn",
        "blog.share_gmail": "Share by Gmail",
        "blog.share_link": "Share / copy link",
        "blog.link_copied": "Link copied!",
        "order.bookmark": "Bookmark this page to check your order's progress anytime.",
        "order.back_home": "← Back to home",
        "login.invalid": "Invalid email or password.",
        "order.title": "Order",
        "order.paid_title": "Payment received — thank you!",
        "order.service": "Service",
        "order.amount": "Amount",
        "order.payment": "Payment",
        "order.status": "Status",
        "order.gateway_error_title": "Online payment isn't available for this order right now.",
        "order.gateway_error_body": "Your order is saved — send us a message and we'll get it sorted.",
        "order.gateway_error_button": "Message us",
        "order.gateway_error_wa_text": "Hi! I just tried to pay for order {order_number} but the payment page did not work.",
        "payment.unpaid": "Unpaid",
        "payment.paid": "Paid",
        "payment.failed": "Failed",
        "payment.refunded": "Refunded",
        "status.pending": "Pending",
        "status.in_progress": "In progress",
        "status.completed": "Completed",
        "status.cancelled": "Cancelled",
        "assistant.label": "Assistant",
        "assistant.title": "Ask us anything",
        "assistant.subtitle": "Quick answers, no waiting",
        "assistant.empty": "No questions yet.",
        "assistant.back": "Back",
        "assistant.close": "Close",
        "error.404_title": "Page not found",
        "error.404_body": "The page you're looking for doesn't exist or has moved.",
        "error.403_title": "Admins only",
        "error.403_body": "You don't have access to this page.",
        "error.500_title": "Something went wrong",
        "error.500_body": "That's on us, not you. Please try again in a moment.",
        "nav.products": "Products",
        "home.trusted_heading": "Trusted by",
        "home.testimonials_heading": "What our clients say",
        "home.view_all_services": "View all services",
        "home.schedule_text": "Hi {site}! I would like to schedule a call to discuss my IT needs.",
        "services.heading": "Our Services",
        "services.intro": "Expert IT help for your home and business.",
        "products.heading": "Products",
        "products.intro": "Quality IT products, set up by us. Send us a message to order.",
        "products.empty": "Products are coming soon — check back shortly.",
        "offer.price_on_request": "Price on request",
        "offer.wa_text": "Hi! I'd like to order: {title} ({price}).",
        "offer.details": "Details",
        "login.subtitle": "For the site owner only.",
        "footer.chat": "Chat with us",
        "offer.order": "Order now",
    },
    "bn": {
        "nav.services": "সার্ভিস",
        "nav.blog": "ব্লগ",
        "footer.tagline": "বাসা ও ব্যবসার জন্য সহজ-সরল আইটি সার্ভিস।",
        "footer.explore": "দেখুন",
        "footer.talk_to_us": "যোগাযোগ করুন",
        "footer.rights": "সর্বস্বত্ব সংরক্ষিত।",
        "home.badge": "বিশ্বস্ত আইটি সার্ভিস, দ্রুত ডেলিভারি",
        "home.title": "কোনো ঝামেলা ছাড়াই দক্ষ আইটি সহায়তা পান।",
        "home.subtitle": "একটা সার্ভিস বেছে নিন আর মেসেজ দিন। বাকিটা আমরা দেখব।",
        "home.browse_services": "সার্ভিস দেখুন",
        "home.chat_with_us": "চ্যাট করুন",
        "home.schedule_call": "কল শিডিউল করুন",
        "home.services_heading": "আমাদের সার্ভিসসমূহ",
        "home.no_services": "সার্ভিস শীঘ্রই আসছে — একটু পর আবার দেখুন।",
        "home.blog_heading": "ব্লগ থেকে",
        "home.view_all": "সব দেখুন →",
        "login.title": "অ্যাডমিন লগ ইন",
        "login.email": "ইমেইল",
        "login.password": "পাসওয়ার্ড",
        "login.submit": "লগ ইন",
        "service.order_now": "এখনই অর্ডার করুন",
        "service.price": "মূল্য",
        "service.back": "← সব সার্ভিস",
        "blog.heading": "মিনা আইটি ব্লগ",
        "blog.empty": "এখনো কোনো লেখা নেই — শীঘ্রই আসছে।",
        "blog.back": "← সব লেখা",
        "blog.learn_more": "বিস্তারিত পড়ুন",
        "blog.search": "ব্লগে খুঁজুন",
        "blog.no_results": "আপনার খোঁজের সাথে মেলে এমন কোনো লেখা নেই।",
        "blog.previous": "আগের",
        "blog.next": "পরের",
        "blog.share_facebook": "ফেসবুকে শেয়ার করুন",
        "blog.share_x": "X-এ শেয়ার করুন",
        "blog.share_linkedin": "লিংকডইনে শেয়ার করুন",
        "blog.share_gmail": "জিমেইলে পাঠান",
        "blog.share_link": "শেয়ার / লিংক কপি করুন",
        "blog.link_copied": "লিংক কপি হয়েছে!",
        "order.bookmark": "যেকোনো সময় অর্ডারের অগ্রগতি দেখতে এই পেজটা বুকমার্ক করে রাখুন।",
        "order.back_home": "← হোমে ফিরে যান",
        "login.invalid": "ইমেইল বা পাসওয়ার্ড ভুল।",
        "order.title": "অর্ডার",
        "order.paid_title": "পেমেন্ট পেয়েছি — ধন্যবাদ!",
        "order.service": "সার্ভিস",
        "order.amount": "পরিমাণ",
        "order.payment": "পেমেন্ট",
        "order.status": "অবস্থা",
        "order.gateway_error_title": "এই মুহূর্তে এই অর্ডারের অনলাইন পেমেন্ট চালু নেই।",
        "order.gateway_error_body": "আপনার অর্ডার সেভ হয়েছে — মেসেজ দিন, আমরা ব্যবস্থা করে দেব।",
        "order.gateway_error_button": "মেসেজ দিন",
        "order.gateway_error_wa_text": "হ্যালো! আমি {order_number} অর্ডারের পেমেন্ট করতে চেয়েছিলাম কিন্তু পেমেন্ট পেজ কাজ করেনি।",
        "payment.unpaid": "বাকি",
        "payment.paid": "পরিশোধিত",
        "payment.failed": "ব্যর্থ",
        "payment.refunded": "ফেরত দেওয়া হয়েছে",
        "status.pending": "অপেক্ষমাণ",
        "status.in_progress": "কাজ চলছে",
        "status.completed": "সম্পন্ন",
        "status.cancelled": "বাতিল",
        "assistant.label": "সহকারী",
        "assistant.title": "যেকোনো প্রশ্ন করুন",
        "assistant.subtitle": "অপেক্ষা ছাড়াই দ্রুত উত্তর",
        "assistant.empty": "এখনো কোনো প্রশ্ন নেই।",
        "assistant.back": "ফিরে যান",
        "assistant.close": "বন্ধ করুন",
        "error.404_title": "পেজটি পাওয়া যায়নি",
        "error.404_body": "আপনি যে পেজটি খুঁজছেন সেটি নেই বা সরিয়ে ফেলা হয়েছে।",
        "error.403_title": "শুধু অ্যাডমিনদের জন্য",
        "error.403_body": "এই পেজ দেখার অনুমতি আপনার নেই।",
        "error.500_title": "কিছু একটা সমস্যা হয়েছে",
        "error.500_body": "সমস্যাটা আমাদের দিকে, আপনার না। একটু পর আবার চেষ্টা করুন।",
        "nav.products": "প্রোডাক্ট",
        "home.trusted_heading": "যাঁরা আমাদের উপর আস্থা রাখেন",
        "home.testimonials_heading": "ক্লায়েন্টরা যা বলেন",
        "home.view_all_services": "সব সার্ভিস দেখুন",
        "home.schedule_text": "হ্যালো {site}! আমার আইটি প্রয়োজন নিয়ে কথা বলতে একটা কল শিডিউল করতে চাই।",
        "services.heading": "আমাদের সার্ভিসসমূহ",
        "services.intro": "বাসা ও ব্যবসার জন্য দক্ষ আইটি সহায়তা।",
        "products.heading": "প্রোডাক্ট",
        "products.intro": "মানসম্পন্ন আইটি প্রোডাক্ট, সেটআপ আমরাই করে দিই। অর্ডার করতে মেসেজ দিন।",
        "products.empty": "প্রোডাক্ট শীঘ্রই আসছে — একটু পর আবার দেখুন।",
        "offer.price_on_request": "দাম জানতে মেসেজ দিন",
        "offer.wa_text": "হ্যালো! আমি অর্ডার করতে চাই: {title} ({price})।",
        "offer.details": "বিস্তারিত",
        "login.subtitle": "শুধু সাইটের মালিকের জন্য।",
        "footer.chat": "চ্যাট করুন",
        "offer.order": "অর্ডার করুন",
    },
}


def get_locale(request: Request) -> str:
    lang = request.cookies.get(LANG_COOKIE)
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def localized(row: dict | None, field: str, locale: str) -> str:
    """Admin-written content (services, FAQs, blog, stats) has an optional
    Bangla copy in a `<field>_bn` column. Show it on the Bangla site when
    it's filled in; otherwise fall back to the main (English) text."""
    if not row:
        return ""
    if locale == "bn" and row.get(f"{field}_bn"):
        return row[f"{field}_bn"]
    return row.get(field) or ""


MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December"],
    "bn": ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই", "আগস্ট",
           "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"],
}
BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def format_date(value: str | None, locale: str) -> str:
    """'2026-08-25T10:00:00+00:00' -> 'August 25, 2026' / '২৫ আগস্ট, ২০২৬'."""
    try:
        year, month, day = (int(p) for p in str(value)[:10].split("-"))
        name = MONTHS.get(locale, MONTHS["en"])[month - 1]
    except (ValueError, IndexError):
        return ""
    if locale == "bn":
        return f"{day} {name}, {year}".translate(BN_DIGITS)
    return f"{name} {day}, {year}"


def make_translator(locale: str):
    table = TRANSLATIONS.get(locale, TRANSLATIONS[DEFAULT_LANG])
    fallback = TRANSLATIONS[DEFAULT_LANG]

    def t(key: str, **values) -> str:
        text = table.get(key) or fallback.get(key) or key
        return text.format(**values) if values else text

    return t
