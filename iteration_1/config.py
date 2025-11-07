# Version 1

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

    # Email server settings (used for sending confirmation or receipt emails)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "25"))
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@charityconnect.local")

    # Suppress email sending by default (useful for local testing)
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "true").lower() == "true"

# Version 1