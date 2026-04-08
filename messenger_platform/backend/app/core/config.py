from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Amline Messenger"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./messenger.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # ── Amline API integration ─────────────────────────────────────────────────
    # Base URL of the Amline backend (e.g. https://api.amline.ir or local)
    amline_base_url: str = "https://api.amline.ir"
    # Admin bearer token obtained after OTP login to Amline
    amline_admin_token: str = ""
    # Whether to auto-sync Amline users as messenger contacts on startup
    amline_sync_on_startup: bool = False

    # Telegram Bot
    telegram_bot_token: str = ""
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_phone: str = ""

    # WhatsApp (unofficial, via whatsapp-web.js wrapper or similar)
    whatsapp_enabled: bool = False

    # Eitaa Bot
    eitaa_token: str = ""

    # Bale Bot
    bale_token: str = ""

    # Rubika (unofficial)
    rubika_enabled: bool = False

    # Rate limiting defaults (messages per platform per 24h)
    telegram_daily_limit: int = 50
    eitaa_daily_limit: int = 200
    bale_daily_limit: int = 100
    rubika_daily_limit: int = 100
    whatsapp_daily_limit: int = 50

    # Admin credentials (for the local messenger admin panel)
    admin_username: str = "admin"
    admin_password: str = "admin123"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
