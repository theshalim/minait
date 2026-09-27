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
-- Row Level Security (defense in depth).
-- The FastAPI backend talks to Postgres with the Supabase SERVICE ROLE key,
-- which bypasses RLS, and enforces auth/admin checks itself in Python.
-- These policies only matter if you ever also call Supabase directly from a
-- browser with the anon key.
-- ---------------------------------------------------------------------------
alter table profiles   enable row level security;
alter table services   enable row level security;
alter table orders     enable row level security;
alter table blog_posts enable row level security;

create policy "profiles: read own" on profiles
  for select using (auth.uid() = id);

create policy "services: public read active" on services
  for select using (is_active = true);

create policy "blog: public read published" on blog_posts
  for select using (is_published = true);

create policy "orders: read own" on orders
  for select using (auth.uid() = user_id);

-- Make the first admin manually after signing up once, e.g.:
-- update profiles set is_admin = true where id = '<your-user-uuid>';
