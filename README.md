# Mina IT Service

Ultra-simple, conversion-focused ordering site for IT services — browse services, order in
under a minute (card, bKash/Nagad, or WhatsApp), track orders from a client dashboard, and run
the whole business from a no-code admin panel.

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
│   │   ├── pages.py         # home, service detail, blog (public)
│   │   ├── auth.py          # signup / login / logout / forgot password
│   │   ├── orders.py        # checkout, order creation, order status
│   │   ├── dashboard.py     # client dashboard
│   │   ├── admin.py         # services/orders/blog/customers (admin only)
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

## 6. Payments

- **Stripe** (international cards): create a restricted/secret key, put it in `STRIPE_SECRET_KEY`.
  Add a webhook endpoint in the Stripe dashboard pointing to
  `https://yourdomain.com/webhooks/stripe` for the `checkout.session.completed` event, and put
  its signing secret in `STRIPE_WEBHOOK_SECRET`. Both are pay-per-transaction — no fixed fee.
- **SSLCOMMERZ** (bKash/Nagad/Rocket/cards, Bangladesh): get sandbox credentials at
  sslcommerz.com, put them in `SSLCOMMERZ_STORE_ID` / `SSLCOMMERZ_STORE_PASSWORD`, keep
  `SSLCOMMERZ_SANDBOX=true` until you go live.
- **WhatsApp**: set `WHATSAPP_NUMBER` (with country code, no `+` or spaces) — customers can
  skip payment gateways entirely and just message you.

## 7. Instant order notifications

Create a Telegram bot via [@BotFather](https://t.me/BotFather), get the bot token and your chat
id (message the bot once, then hit `https://api.telegram.org/bot<token>/getUpdates`), and set
`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`. Optionally also set `DISCORD_WEBHOOK_URL`. You'll get
a push the second an order is placed or paid.

## 8. No emails: passwords and customer updates go through WhatsApp

The site sends no email (free-tier mail limits make it unreliable), so:

- **Forgot password:** the login page links to `/forgot-password`. The customer types their
  email, the admin gets a Telegram/Discord alert and the customer is taken to WhatsApp. The
  admin opens **Admin → Customers**, sets a new password, and presses **Send on WhatsApp**.
  Logged-in customers can change their own password from their dashboard.
- **Order updates:** in **Admin → Orders**, the **WhatsApp customer** button opens a chat with
  the customer, with the order's current status already written in Bangla and English. Checkout
  asks for the phone (WhatsApp) number for this reason.
- **WhatsApp / cash payments:** set the order's **Payment** to *Paid* in **Admin → Orders**
  so it counts in the dashboard revenue.

## 9. Bangla content

Services, blog posts, FAQs and stat counters have optional Bangla fields in the admin panel.
Visitors on the বাংলা site see the Bangla text when it is filled in, otherwise the English text.
These columns come from `db/schema.sql`; **re-run it in the Supabase SQL editor after updating**
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
- Order pages are reachable via their unguessable `order_number` without login, so a guest
  checkout still gets a working "track my order" link (like a receipt link).
