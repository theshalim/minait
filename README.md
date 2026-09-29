# Mina IT Service

Minimal, conversion-focused site for IT services and products — visitors browse, then order
by chatting on WhatsApp. One admin runs everything (orders, services, products, homepage,
client testimonials and logos, blog, FAQs) from a no-code admin panel.

**Stack:** FastAPI (Python serverless) · Jinja2 + Tailwind CSS (CDN, no build step) · Supabase
(Postgres + Auth) · Stripe & SSLCOMMERZ · Telegram/Discord instant notifications · Vercel Hobby
(free) hosting.

## 1. Folder structure

```
minait/
├── api/
│   └── index.py            # Vercel entrypoint — exports the FastAPI app
├── app/
│   ├── main.py              # app factory, routers, static mount, error pages
│   ├── config.py            # reads env vars
│   ├── supabase_client.py   # admin (service role) + auth (anon) Supabase clients
│   ├── security.py          # session cookies, get_current_user, require_admin
│   ├── payments.py          # Stripe Checkout + SSLCOMMERZ integration
│   ├── notify.py            # Telegram / Discord instant admin notifications
│   ├── utils.py             # slugify, order numbers, markdown rendering
│   ├── routers/
│   │   ├── pages.py         # home, services, products, blog (public)
│   │   ├── auth.py          # admin login / logout
│   │   ├── orders.py        # order tracking page (+ old checkout links → WhatsApp)
│   │   ├── admin.py         # the whole admin panel
│   │   └── webhooks.py      # Stripe + SSLCOMMERZ payment confirmations
│   ├── templates/           # Jinja2 templates (Tailwind via CDN)
│   └── static/              # css/js served at /static
├── tests/                  # pytest suite (fake Supabase, no keys needed)
├── db/
│   └── schema.sql           # run once in Supabase/Neon SQL editor
├── vercel.json
├── requirements.txt
└── .env.example
```

## 2. Database setup (Supabase, free tier)

1. Create a free project at supabase.com.
2. Open the SQL editor and run [`db/schema.sql`](db/schema.sql).
3. Copy **Project Settings → API**: `URL`, `anon public` key, `service_role` key into your `.env`.
4. Sign up once through the site, then in the SQL editor run:
   ```sql
   update profiles set is_admin = true where id = '<your-user-uuid-from-auth.users>';
   ```
   That account now has access to `/admin`.
5. Optional: run [`db/sample_content.sql`](db/sample_content.sql) too, for 4 sample services,
   4 products and 4 blog posts (free Unsplash photos) so the site doesn't start empty. Edit or
   delete them in the admin panel later.
7. Optional: run [`db/service_basket.sql`](db/service_basket.sql) for the "Our Service Basket"
   group (custom software, web development & maintenance, cloud management, IT infrastructure),
   written for Bangladeshi businesses, in English and Bangla.
6. Optional: run [`db/sample_faqs.sql`](db/sample_faqs.sql) for 35 plain-language FAQs (English +
   Bangla, grouped by topic) for the "?" assistant. Adjust prices, timelines and payment terms
   in **Admin → FAQs** to match how you really work.

(Using plain Neon Postgres instead of Supabase Auth is possible but requires swapping
`app/security.py` for your own JWT/password-hash login — Supabase is the path of least
resistance for the free-tier + built-in-auth requirement.)

## 3. Environment variables

Copy `.env.example` to `.env` locally, and add the same keys under **Vercel → Project →
Settings → Environment Variables** for production. Never commit `.env`.

## 4. Local development

```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Visit http://localhost:8000

## 5. Deploy to Vercel (free Hobby plan)

```bash
npm i -g vercel
vercel        # first deploy, follow prompts
vercel --prod
```
`vercel.json` routes every request to `api/index.py`, which is auto-detected as an ASGI app —
no extra config needed.

## 6. Ordering and payments

- No prices are shown on the site. Every **Order now** / **Book a demo** button opens a short
  form (`/order/service/<slug>` or `/order/product/<slug>?type=demo`): name, email or phone,
  company and details. The request lands in **Admin → Orders** (demo requests are marked) and
  the admin gets a Telegram/Discord alert. The form page also offers call / email / chat.
- Products show as a slider on the homepage and `/products`: two at a time (one on phones), a
  picture box over a details box, in soft colours. The slide speed is set in
  **Admin → Products**, the colour per product in its edit form.
- Orders that come by phone or chat are added in **Admin → Orders → + Add order**. Mark them
  *Paid* when the money arrives (so they count in revenue) and send the customer their status +
  tracking link with the **WhatsApp customer** button.
- The Stripe / SSLCOMMERZ code (`app/payments.py`, `app/routers/webhooks.py`) is kept but not
  linked from the site.
- The footer's **Talk to us** shows Chat (WhatsApp), the email and the phone number set in
  **Admin → Home page → Contact info**.

## 7. Instant order notifications

Create a Telegram bot via [@BotFather](https://t.me/BotFather), get the bot token and your chat
id (message the bot once, then hit `https://api.telegram.org/bot<token>/getUpdates`), and set
`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`. Optionally also set `DISCORD_WEBHOOK_URL`. You'll get
a push the second an order is placed or paid.

## 8. The admin account

- There is **one admin** and no customer accounts. There is no login link on the site: open
  `https://yourdomain.com/login` (or `/admin`) by typing the URL. `/signup` is closed.
- Change the password in **Admin → Account**. Forgot it? Supabase dashboard →
  Authentication → Users → the admin user → *Send password recovery* or set a new one there
  (the site itself sends no email).

## 9. Bangla content

Services, blog posts, FAQs and stat counters have optional Bangla fields in the admin panel.
Visitors on the বাংলা site see the Bangla text when it is filled in, otherwise the English text.
The blog's "top post", the products / testimonials / client-logo tables and these columns
come from `db/schema.sql`; **re-run it in the Supabase SQL editor after updating**
(it is safe to re-run and only adds what is missing).

## 10. Tests

The tests run the whole app against an in-memory fake of Supabase, so they need no keys or
internet:

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

## 11. Notes & next steps

- Tailwind is loaded via the CDN `<script>` for a zero-build deploy that fits the free-tier
  constraint end to end. For a production performance pass, swap it for a compiled Tailwind
  build served from `/static/css`.
- Admin role is a manual DB flag (`profiles.is_admin`) rather than an invite flow, kept simple
  on purpose — promote trusted accounts via SQL as shown above.
- Order pages are reachable via their unguessable `order_number` without login, so the
  tracking link the admin sends on WhatsApp works for the customer (like a receipt link).
