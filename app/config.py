"""Central place for reading configuration from environment variables.

On Vercel, set these under Project Settings -> Environment Variables.
Locally, copy .env.example to .env and fill it in.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


class Settings:
    # Supabase
    SUPABASE_URL: str = _env("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = _env("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = _env("SUPABASE_SERVICE_ROLE_KEY")

    # App
    APP_SECRET_KEY: str = _env("APP_SECRET_KEY", "dev-secret-change-me")
    SITE_URL: str = _env("SITE_URL", "http://localhost:8000")
    SITE_NAME: str = "Mina IT Service"

    # Stripe
    STRIPE_SECRET_KEY: str = _env("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str = _env("STRIPE_WEBHOOK_SECRET")

    # SSLCOMMERZ
    SSLCOMMERZ_STORE_ID: str = _env("SSLCOMMERZ_STORE_ID")
    SSLCOMMERZ_STORE_PASSWORD: str = _env("SSLCOMMERZ_STORE_PASSWORD")
    SSLCOMMERZ_SANDBOX: bool = _env("SSLCOMMERZ_SANDBOX", "true").lower() == "true"

    # Direct communication
    WHATSAPP_NUMBER: str = _env("WHATSAPP_NUMBER")

    # Notifications
    TELEGRAM_BOT_TOKEN: str = _env("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = _env("TELEGRAM_CHAT_ID")
    DISCORD_WEBHOOK_URL: str = _env("DISCORD_WEBHOOK_URL")


settings = Settings()
