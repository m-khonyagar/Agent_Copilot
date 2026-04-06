from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db, AsyncSessionLocal
from app.api.contacts import router as contacts_router
from app.api.messages import router as messages_router
from app.api.admin import router as admin_router
from app.services.scheduler import run_pending_sends
from app.services.amline_sync import sync_contacts_from_amline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialised")

    # Optionally pull Amline users into local contacts on startup
    if settings.amline_sync_on_startup:
        async with AsyncSessionLocal() as db:
            synced = await sync_contacts_from_amline(db)
            logger.info("Startup Amline sync: %d contacts imported", synced)

    task = asyncio.create_task(_scheduler_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def _scheduler_loop():
    """Tick every 60 seconds to dispatch pending scheduled sends."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await run_pending_sends(db)
        except Exception:
            logger.exception("Scheduler tick failed")
        await asyncio.sleep(60)


app = FastAPI(
    title="Amline Messenger API",
    version="1.0.0",
    description=(
        "پیام‌رسان چند-کاناله املاین — بررسی اکانت مخاطبان، ارسال پیام تکی و انبوه، "
        "تاریخچه تعاملات و یکپارچه‌سازی با پلتفرم اصلی امَلاین (amline.ir). "
        "Platforms: Telegram, Eitaa, Bale, WhatsApp, Rubika."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts_router)
app.include_router(messages_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"status": "ok", "app": settings.app_name, "platform": "amline.ir"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
