from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AMLINE_", env_file=".env", extra="ignore")

    env: str = "dev"

    database_url: str
    redis_url: str

    jwt_secret: str
    jwt_issuer: str = "amline"
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 30

    s3_endpoint_url: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str = "amline-docs"
    s3_region: str = "us-east-1"

    otp_ttl_seconds: int = 120

    # PDF Generator service URL
    pdf_generator_url: str = "http://pdf-generator:8000"

    # CSV: CODE:percent_off_total (e.g. AMLINE50:50). Empty = no promotional codes.
    commission_discount_codes: str = ""

    # Notification worker settings
    notification_max_attempts: int = 5
    notification_retry_base_seconds: int = 5
    notification_retry_max_seconds: int = 300
    notification_stuck_ms: int = 60000

    # Dev convenience: if set, this mobile becomes Admin on login.
    bootstrap_admin_mobile: str | None = None

    # OTP ثابت برای تست لوکال/استیجینگ (و دمو آنلاین با فلگ صریح)
    # در production فقط وقتی true است که روی سرور عمداً فعال کرده باشید.
    fixed_test_otp_enabled: bool = False
    fixed_test_mobile: str = "09100000000"
    fixed_test_otp: str = "11111"

    # ── ONLYOFFICE Document Server integration ──────────────────────────────
    # JWT secret shared between the backend and ONLYOFFICE Document Server.
    # Must match the JWT_SECRET env var set on the ONLYOFFICE container.
    # Generate with: openssl rand -hex 32
    onlyoffice_jwt_secret: str = "change-me-onlyoffice-secret"

    # Public URL of the ONLYOFFICE Document Server (used by the browser to load
    # the JS SDK and open documents).
    onlyoffice_server_url: str = "http://localhost:8180"

    # Base URL that ONLYOFFICE will call back to after saving a document.
    # Must be reachable from inside the Docker network (e.g. http://backend:8000).
    # If None, the backend will use its own request.base_url as a fallback.
    onlyoffice_callback_base_url: str | None = None


settings = Settings()
