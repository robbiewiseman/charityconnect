# VERSION 1

# This file stores all configuration settings for the CharityConnect Flask application.
import os
from dotenv import load_dotenv

# Load environment variables from the .env file (e.g., database URL, secret key, etc.)
load_dotenv()

class Config:
    # Security key used by Flask and WTForms for session and CSRF protection
    # Reference: Flask config & SECRET_KEY usage (Pallets Projects, 2024)
    # https://flask.palletsprojects.com/en/stable/config/
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # Database connection string (defaults to local SQLite if not set in .env)
    # Reference: Neon env var + fallback to SQLite (Neon Tech; PostgreSQL, 2025)
    # https://neon.com/docs/guides/environment-variables
    # https://www.postgresql.org/docs/current/libpq-envars.html
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///charityconnect.db")

    # Disable SQLAlchemy's event system to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # VERSION 2 START
    # Reference: Stripe API key handling follows Stripe’s security guidance to store keys securely
    # Url: https://docs.stripe.com/keys
    # Stripe API keys loaded from environment variables
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    # Database engine settings to keep connections healthy and stable
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,   # checks connections before using them to avoid stale connections
    "pool_recycle": 300,    # refresh connections every 5 minutes (helps with long-lived DB sessions)
    "pool_size": 5,   # base number of open DB connections  
    "max_overflow": 10,   # extra connections allowed during spikes in activity
}
    # VERSION 2 END

    # VERSION 3 START
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "arcee-ai/trinity-large-preview:free")
    OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://127.0.0.1:5000")
    OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "CharityConnect")
    # VERSION 3 END

    # VERSION 4 START
    # Reference: Gmail SMTP settings and TLS configuration (Google, 2024)
    # https://support.google.com/mail/answer/7126229
    # https://seatable.com/help/setup-gmail-smtp-email-seatable/
    # Email (SMTP) config
    MAIL_SERVER = os.getenv("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "0") == "1"

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_FROM",
        "CharityConnect <no-reply@charityconnect.ie>"
    )
    # VERSION 4 END


# VERSION 1