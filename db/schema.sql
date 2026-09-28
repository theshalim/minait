-- Mina IT Service — database schema (PostgreSQL / Supabase / Neon)
-- Run this once in your database's SQL editor.
-- Auth (auth.users) is managed by Supabase Auth. If you are on plain Neon/Postgres
-- without Supabase Auth, replace the `references auth.users(id)` lines with a
-- self-managed `users` table (id uuid primary key, email text, password_hash text, ...).

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- profiles: one row per authenticated user, extends auth.users
-- ---------------------------------------------------------------------------
create table if not exists profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  full_name   text,
  phone       text,
  is_admin    boolean not null default false,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- services: catalog of IT services offered
-- ---------------------------------------------------------------------------
create table if not exists services (
  id          bigserial primary key,
  title       text not null,
  slug        text not null unique,
  description text not null default '',
  price       numeric(10, 2) not null,
  currency    text not null default 'BDT',
  category    text not null default 'General',
  icon        text,               -- emoji or icon class shown on the card
  image_url   text,               -- optional hero image for the service page
  is_active   boolean not null default true,
  sort_order  integer not null default 0,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create index if not exists idx_services_active on services (is_active, sort_order);

-- ---------------------------------------------------------------------------
-- orders: every order placed through the site
-- ---------------------------------------------------------------------------
create table if not exists orders (
  id              bigserial primary key,
  order_number    text not null unique,             -- human readable, e.g. MINA-000123
  user_id         uuid references auth.users(id) on delete set null,
  service_id      bigint references services(id) on delete set null,
  service_title   text not null,                    -- snapshot at order time
  customer_name   text not null,
  customer_email  text not null,
  customer_phone  text,
  notes           text,
  amount          numeric(10, 2) not null,
  currency        text not null default 'BDT',
  payment_method  text not null default 'whatsapp',  -- 'stripe' | 'sslcommerz' | 'whatsapp'
  payment_status  text not null default 'unpaid',    -- 'unpaid' | 'paid' | 'failed' | 'refunded'
  payment_ref     text,                              -- gateway session/transaction id
  status          text not null default 'pending',   -- 'pending' | 'in_progress' | 'completed' | 'cancelled'
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

create index if not exists idx_orders_user on orders (user_id);
create index if not exists idx_orders_status on orders (status);

-- ---------------------------------------------------------------------------
-- blog_posts: simple markdown-driven blog
-- ---------------------------------------------------------------------------
create table if not exists blog_posts (
  id                bigserial primary key,
  title             text not null,
  slug              text not null unique,
  excerpt           text,
  content_markdown  text not null,
  cover_image_url   text,
  is_published      boolean not null default false,
  author_id         uuid references auth.users(id) on delete set null,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

create index if not exists idx_blog_published on blog_posts (is_published, created_at desc);

-- ---------------------------------------------------------------------------
-- hero_slides: the homepage hero carousel — however many slides are added
-- (and marked active) here, that's how many the homepage shows.
-- ---------------------------------------------------------------------------
create table if not exists hero_slides (
  id            bigserial primary key,
  image_url     text not null,
  heading       text not null,
  subheading    text,
  button_label  text,               -- e.g. "Browse services" — optional
  button_url    text,               -- e.g. "/#services" or a full URL
  is_active     boolean not null default true,
  sort_order    integer not null default 0,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create index if not exists idx_hero_slides_active on hero_slides (is_active, sort_order);

-- ---------------------------------------------------------------------------
-- site_stats: the small "2 IT experts / 1 office / 10 clients served"
-- style counters on the homepage — also an open-ended list.
-- ---------------------------------------------------------------------------
create table if not exists site_stats (
  id          bigserial primary key,
  label       text not null,        -- e.g. "Clients served"
  value       text not null,        -- e.g. "10+" — plain text, so "24/7" etc. work too
  sort_order  integer not null default 0,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- faqs: pre-written question/answer pairs shown in the floating "Assistant"
-- chat widget (site-wide). Not real AI — a simple, admin-managed FAQ list.
-- ---------------------------------------------------------------------------
create table if not exists faqs (
  id          bigserial primary key,
  question    text not null,
  answer      text not null,
  sort_order  integer not null default 0,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- products: items sold (ordered on WhatsApp, like services). Price is
-- optional — empty shows "Price on request".
-- ---------------------------------------------------------------------------
create table if not exists products (
  id             bigserial primary key,
  title          text not null,
  title_bn       text,
  slug           text not null unique,
  description    text not null default '',
  description_bn text,
  price          numeric(10, 2),
  currency       text not null default 'BDT',
  category       text not null default '',
  image_url      text,
  is_active      boolean not null default true,
  sort_order     integer not null default 0,
  created_at     timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- testimonials: the "What our clients say" cards on the homepage.
-- ---------------------------------------------------------------------------
create table if not exists testimonials (
  id          bigserial primary key,
  name        text not null,             -- e.g. "Rahim Uddin"
  role        text,                      -- e.g. "CEO, ABC Traders"
  role_bn     text,
  message     text not null,
  message_bn  text,
  image_url   text,                      -- client photo or company logo
  is_active   boolean not null default true,
  sort_order  integer not null default 0,
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- clients: logos in the always-moving "Trusted by" strip on the homepage.
-- ---------------------------------------------------------------------------
create table if not exists clients (
  id           bigserial primary key,
  name         text not null,
  logo_url     text,
  website_url  text,
  sort_order   integer not null default 0,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- features: the "Why choose us" points on the homepage. Four starter points
-- are added the first time this runs (edit or delete them in the admin).
-- ---------------------------------------------------------------------------
create table if not exists features (
  id             bigserial primary key,
  title          text not null,
  title_bn       text,
  description    text not null default '',
  description_bn text,
  sort_order     integer not null default 0,
  created_at     timestamptz not null default now()
);

insert into features (title, title_bn, description, description_bn, sort_order)
select * from (values
  ('Same-day support', 'একই দিনে সাপোর্ট',
   'Tell us the problem in the morning, it''s usually fixed the same day.',
   'সকালে সমস্যা জানালে সাধারণত সেদিনই সমাধান করে দিই।', 1),
  ('Experienced team', 'অভিজ্ঞ টিম',
   'Certified engineers who have set up offices, shops and homes.',
   'অফিস, দোকান ও বাসায় কাজ করা দক্ষ ইঞ্জিনিয়ার।', 2),
  ('Clear pricing', 'স্বচ্ছ দাম',
   'You know the price before we start. No hidden charges.',
   'কাজ শুরুর আগেই দাম জানবেন। কোনো লুকানো খরচ নেই।', 3),
  ('After-service care', 'কাজের পরেও পাশে',
   'Warranty on our work and quick help if anything goes wrong later.',
   'কাজের ওয়ারেন্টি, আর পরে কোনো সমস্যা হলে দ্রুত সহায়তা।', 4)
) as v(title, title_bn, description, description_bn, sort_order)
where not exists (select 1 from features);

-- ---------------------------------------------------------------------------
-- site_settings: small admin-editable values, e.g. the footer's contact
-- email and phone (Admin -> Home page -> Contact info).
-- ---------------------------------------------------------------------------
create table if not exists site_settings (
  key    text primary key,
  value  text not null default ''
);

-- ---------------------------------------------------------------------------
-- Optional Bangla copies of admin-written content. Shown on the বাংলা site
-- when filled in; empty means "show the English text there too".
-- Safe to re-run: existing databases just gain the new columns.
-- ---------------------------------------------------------------------------
alter table services   add column if not exists title_bn            text;
alter table services   add column if not exists description_bn      text;
alter table blog_posts add column if not exists title_bn            text;
alter table blog_posts add column if not exists excerpt_bn          text;
alter table blog_posts add column if not exists content_markdown_bn text;
alter table faqs       add column if not exists question_bn         text;
alter table faqs       add column if not exists answer_bn           text;
alter table site_stats add column if not exists label_bn            text;

-- Services are grouped by category on the Services page; this is the
-- group name on the Bangla site.
alter table services add column if not exists category_bn text;

-- Product card colour on the site: '' = automatic, or blue / green / rose /
-- amber / violet / teal.
alter table products add column if not exists color text not null default '';

-- What a visitor asked for through the website form: 'order' or 'demo'.
alter table orders add column if not exists kind text not null default 'order';

-- The one blog post the admin picked to show big at the top of /blog.
alter table blog_posts add column if not exists is_featured boolean not null default false;

-- ---------------------------------------------------------------------------
-- Row Level Security (defense in depth).
-- The FastAPI backend talks to Postgres with the Supabase SERVICE ROLE key,
-- which bypasses RLS, and enforces auth/admin checks itself in Python.
-- These policies only matter if you ever also call Supabase directly from a
-- browser with the anon key.
-- ---------------------------------------------------------------------------
alter table profiles    enable row level security;
alter table services    enable row level security;
alter table orders      enable row level security;
alter table blog_posts  enable row level security;
alter table hero_slides enable row level security;
alter table site_stats  enable row level security;
alter table faqs        enable row level security;
alter table products     enable row level security;
alter table testimonials enable row level security;
alter table clients      enable row level security;
alter table site_settings enable row level security;
alter table features      enable row level security;

drop policy if exists "features: public read" on features;
create policy "features: public read" on features
  for select using (true);

drop policy if exists "site_settings: public read" on site_settings;
create policy "site_settings: public read" on site_settings
  for select using (true);

drop policy if exists "products: public read active" on products;
create policy "products: public read active" on products
  for select using (is_active = true);

drop policy if exists "testimonials: public read active" on testimonials;
create policy "testimonials: public read active" on testimonials
  for select using (is_active = true);

drop policy if exists "clients: public read" on clients;
create policy "clients: public read" on clients
  for select using (true);

drop policy if exists "profiles: read own" on profiles;
create policy "profiles: read own" on profiles
  for select using (auth.uid() = id);

drop policy if exists "services: public read active" on services;
create policy "services: public read active" on services
  for select using (is_active = true);

drop policy if exists "blog: public read published" on blog_posts;
create policy "blog: public read published" on blog_posts
  for select using (is_published = true);

drop policy if exists "orders: read own" on orders;
create policy "orders: read own" on orders
  for select using (auth.uid() = user_id);

drop policy if exists "hero_slides: public read active" on hero_slides;
create policy "hero_slides: public read active" on hero_slides
  for select using (is_active = true);

drop policy if exists "site_stats: public read" on site_stats;
create policy "site_stats: public read" on site_stats
  for select using (true);

drop policy if exists "faqs: public read" on faqs;
create policy "faqs: public read" on faqs
  for select using (true);

-- Make the first admin manually after signing up once, e.g.:
-- update profiles set is_admin = true where id = '<your-user-uuid>';
