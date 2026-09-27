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
        "nav.how_it_works": "How it works",
        "nav.blog": "Blog",
        "nav.login": "Log in",
        "nav.signup": "Sign up",
        "nav.admin": "Admin",
        "nav.dashboard": "Dashboard",
        "nav.logout": "Logout",
        "footer.tagline": "Straightforward IT services, ordered online in minutes.",
        "footer.explore": "Explore",
        "footer.talk_to_us": "Talk to us",
        "footer.chat_whatsapp": "Chat on WhatsApp",
        "footer.rights": "All rights reserved.",
        "home.badge": "Trusted IT services, delivered fast",
        "home.title": "Get expert IT help without the runaround.",
        "home.subtitle": "Pick a service, tell us what you need, and pay securely — or just message us on WhatsApp. That's it.",
        "home.browse_services": "Browse services",
        "home.chat_with_us": "Chat with us",
        "home.schedule_call": "Schedule a Call",
        "home.services_heading": "Our Services",
        "home.services_sub": "Clear pricing. No surprises.",
        "home.no_services": "Services are coming soon — check back shortly.",
        "home.order_now": "Order now →",
        "home.how_it_works_heading": "How it works",
        "home.how_it_works_sub": "Three steps. No confusion.",
        "home.step1_title": "Choose a service",
        "home.step1_desc": "Browse our catalog and pick exactly what you need.",
        "home.step2_title": "Order in minutes",
        "home.step2_desc": "Fill a short form, or just message us on WhatsApp.",
        "home.step3_title": "We get to work",
        "home.step3_desc": "Pay securely and track progress from your dashboard.",
        "home.blog_heading": "From the blog",
        "home.view_all": "View all →",
        "checkout.title": "Complete your order",
        "checkout.full_name": "Full name",
        "checkout.email": "Email",
        "checkout.phone": "Phone",
        "checkout.notes": "Notes",
        "checkout.optional": "(optional)",
        "checkout.payment_method": "How would you like to proceed?",
        "checkout.pay_card": "Pay by card (Stripe)",
        "checkout.pay_local": "bKash / Nagad / Rocket (SSLCOMMERZ)",
        "checkout.pay_whatsapp": "Just message us on WhatsApp",
        "checkout.confirm_order": "Confirm order",
        "login.title": "Welcome back",
        "login.email": "Email",
        "login.password": "Password",
        "login.submit": "Log in",
        "login.no_account": "New here?",
        "login.create_account": "Create an account",
        "signup.title": "Create your account",
        "signup.full_name": "Full name",
        "signup.email": "Email",
        "signup.phone": "Phone",
        "signup.password": "Password",
        "signup.submit": "Create account",
        "signup.have_account": "Already have an account?",
        "signup.log_in": "Log in",
        "dashboard.subtitle": "Here's everything you've ordered with us.",
        "dashboard.no_orders": "You haven't placed any orders yet.",
        "dashboard.browse": "Browse services →",
        "service.order_now": "Order Now",
        "service.price": "Price",
        "service.back": "← All services",
        "blog.heading": "Blog",
        "blog.empty": "No articles yet — check back soon.",
        "blog.back": "← All articles",
        "order.bookmark": "Bookmark this page to check progress anytime. A copy was sent to",
        "order.back_home": "← Back to home",
    },
    "bn": {
        "nav.services": "সার্ভিস",
        "nav.how_it_works": "যেভাবে কাজ করে",
        "nav.blog": "ব্লগ",
        "nav.login": "লগ ইন",
        "nav.signup": "সাইন আপ",
        "nav.admin": "অ্যাডমিন",
        "nav.dashboard": "ড্যাশবোর্ড",
        "nav.logout": "লগ আউট",
        "footer.tagline": "সহজ-সরল আইটি সার্ভিস, মিনিটেই অনলাইনে অর্ডার করুন।",
        "footer.explore": "দেখুন",
        "footer.talk_to_us": "যোগাযোগ করুন",
        "footer.chat_whatsapp": "হোয়াটসঅ্যাপে চ্যাট করুন",
        "footer.rights": "সর্বস্বত্ব সংরক্ষিত।",
        "home.badge": "বিশ্বস্ত আইটি সার্ভিস, দ্রুত ডেলিভারি",
        "home.title": "কোনো ঝামেলা ছাড়াই দক্ষ আইটি সহায়তা পান।",
        "home.subtitle": "একটা সার্ভিস বেছে নিন, আপনার প্রয়োজন জানান, নিরাপদে পেমেন্ট করুন — অথবা শুধু হোয়াটসঅ্যাপে মেসেজ দিন। ব্যাস, এতটুকুই।",
        "home.browse_services": "সার্ভিস দেখুন",
        "home.chat_with_us": "চ্যাট করুন",
        "home.schedule_call": "কল শিডিউল করুন",
        "home.services_heading": "আমাদের সার্ভিসসমূহ",
        "home.services_sub": "স্পষ্ট মূল্য। কোনো লুকোচুরি নেই।",
        "home.no_services": "সার্ভিস শীঘ্রই আসছে — একটু পর আবার দেখুন।",
        "home.order_now": "এখনই অর্ডার করুন →",
        "home.how_it_works_heading": "যেভাবে কাজ করে",
        "home.how_it_works_sub": "তিনটা ধাপ। কোনো জটিলতা নেই।",
        "home.step1_title": "একটা সার্ভিস বেছে নিন",
        "home.step1_desc": "আমাদের ক্যাটালগ ঘুরে দেখুন, ঠিক যা দরকার তা বেছে নিন।",
        "home.step2_title": "মিনিটেই অর্ডার করুন",
        "home.step2_desc": "ছোট্ট একটা ফর্ম পূরণ করুন, অথবা শুধু হোয়াটসঅ্যাপে মেসেজ দিন।",
        "home.step3_title": "আমরা কাজ শুরু করি",
        "home.step3_desc": "নিরাপদে পেমেন্ট করুন, ড্যাশবোর্ড থেকে অগ্রগতি দেখুন।",
        "home.blog_heading": "ব্লগ থেকে",
        "home.view_all": "সব দেখুন →",
        "checkout.title": "আপনার অর্ডার সম্পূর্ণ করুন",
        "checkout.full_name": "পুরো নাম",
        "checkout.email": "ইমেইল",
        "checkout.phone": "ফোন",
        "checkout.notes": "নোট",
        "checkout.optional": "(ঐচ্ছিক)",
        "checkout.payment_method": "কীভাবে এগোতে চান?",
        "checkout.pay_card": "কার্ডে পেমেন্ট (Stripe)",
        "checkout.pay_local": "বিকাশ / নগদ / রকেট (SSLCOMMERZ)",
        "checkout.pay_whatsapp": "শুধু হোয়াটসঅ্যাপে মেসেজ দিন",
        "checkout.confirm_order": "অর্ডার কনফার্ম করুন",
        "login.title": "আবার স্বাগতম",
        "login.email": "ইমেইল",
        "login.password": "পাসওয়ার্ড",
        "login.submit": "লগ ইন",
        "login.no_account": "নতুন এসেছেন?",
        "login.create_account": "অ্যাকাউন্ট তৈরি করুন",
        "signup.title": "আপনার অ্যাকাউন্ট তৈরি করুন",
        "signup.full_name": "পুরো নাম",
        "signup.email": "ইমেইল",
        "signup.phone": "ফোন",
        "signup.password": "পাসওয়ার্ড",
        "signup.submit": "অ্যাকাউন্ট তৈরি করুন",
        "signup.have_account": "আগে থেকেই অ্যাকাউন্ট আছে?",
        "signup.log_in": "লগ ইন করুন",
        "dashboard.subtitle": "আপনার সব অর্ডারের তালিকা এখানে।",
        "dashboard.no_orders": "আপনি এখনো কোনো অর্ডার করেননি।",
        "dashboard.browse": "সার্ভিস দেখুন →",
        "service.order_now": "এখনই অর্ডার করুন",
        "service.price": "মূল্য",
        "service.back": "← সব সার্ভিস",
        "blog.heading": "ব্লগ",
        "blog.empty": "এখনো কোনো লেখা নেই — শীঘ্রই আসছে।",
        "blog.back": "← সব লেখা",
        "order.bookmark": "অগ্রগতি দেখতে এই পেজটা বুকমার্ক করে রাখুন। একটা কপি পাঠানো হয়েছে",
        "order.back_home": "← হোমে ফিরে যান",
    },
}


def get_locale(request: Request) -> str:
    lang = request.cookies.get(LANG_COOKIE)
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def make_translator(locale: str):
    table = TRANSLATIONS.get(locale, TRANSLATIONS[DEFAULT_LANG])
    fallback = TRANSLATIONS[DEFAULT_LANG]

    def t(key: str) -> str:
        return table.get(key) or fallback.get(key) or key

    return t
