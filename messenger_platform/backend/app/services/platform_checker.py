"""
Platform account checker service.

Each checker probes whether a phone number has an account on a given
messaging platform and, where the API allows it, retrieves the user's
last-seen / online timestamp.

Design principles
-----------------
* All checkers are *async* so the FastAPI event loop is never blocked.
* Real network calls are only made when valid credentials are configured;
  otherwise the function returns a "unknown / unconfigured" result so the
  application can still start without every token being set.
* Error handling is intentionally defensive: a network failure or an
  unexpected API response is reported as has_account=None (unknown) rather
  than crashing the caller.

Platform notes
--------------
Telegram  – uses the official MTProto API via Telethon (requires
            api_id + api_hash + a logged-in phone session).
WhatsApp  – no public API; marked as not-supported in this service layer.
Eitaa     – uses the public Eitaa Bot API (https://eitaa.com/botapi).
            Bot API does not expose a "does this number have an account"
            endpoint, so we return unknown.
Bale      – uses the Bale Bot API (similar to Telegram Bot API).
            Same limitation as Eitaa.
Rubika    – no public API; marked as not-supported.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AccountInfo:
    def __init__(
        self,
        platform: str,
        phone: str,
        has_account: Optional[bool],
        username: Optional[str] = None,
        last_online: Optional[datetime] = None,
        error: Optional[str] = None,
    ):
        self.platform = platform
        self.phone = phone
        self.has_account = has_account
        self.username = username
        self.last_online = last_online
        self.error = error


async def check_telegram(phone: str) -> AccountInfo:
    """
    Check whether a phone number has a Telegram account and retrieve its
    last-seen timestamp.  Requires TELEGRAM_API_ID, TELEGRAM_API_HASH and a
    pre-authorised session file (session name == 'messenger_session').
    """
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        return AccountInfo("telegram", phone, None, error="Telegram API credentials not configured")

    try:
        from telethon import TelegramClient
        from telethon.errors import FloodWaitError
        from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently

        client = TelegramClient("messenger_session", settings.telegram_api_id, settings.telegram_api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()
            return AccountInfo("telegram", phone, None, error="Telegram session not authorised")

        try:
            contact = await client.get_entity(phone)
        except Exception as exc:
            await client.disconnect()
            if "phone" in str(exc).lower() or "not found" in str(exc).lower():
                return AccountInfo("telegram", phone, False)
            return AccountInfo("telegram", phone, None, error=str(exc))

        last_online: Optional[datetime] = None
        if hasattr(contact, "status"):
            status = contact.status
            if isinstance(status, UserStatusOnline):
                last_online = datetime.now(timezone.utc)
            elif isinstance(status, UserStatusOffline):
                last_online = status.was_online
            elif isinstance(status, UserStatusRecently):
                last_online = None  # hidden by privacy settings

        username = getattr(contact, "username", None)
        await client.disconnect()
        return AccountInfo("telegram", phone, True, username=username, last_online=last_online)

    except Exception as exc:
        logger.exception("Telegram check failed for %s", phone)
        return AccountInfo("telegram", phone, None, error=str(exc))


async def check_eitaa(phone: str) -> AccountInfo:
    """
    Eitaa Bot API does not expose a membership-check endpoint.
    Returns has_account=None (unknown) unless a bot token is configured,
    in which case the answer is still unknown but we record the attempt.
    """
    if not settings.eitaa_token:
        return AccountInfo("eitaa", phone, None, error="Eitaa token not configured")
    # Eitaa API mirrors Telegram Bot API at https://eitaa.com/BotAPI
    url = f"https://eitaa.com/BotAPI/bot{settings.eitaa_token}/getMe"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return AccountInfo("eitaa", phone, None, error="Eitaa does not expose account-check endpoint")
    except Exception as exc:
        logger.exception("Eitaa check failed for %s", phone)
        return AccountInfo("eitaa", phone, None, error=str(exc))
    return AccountInfo("eitaa", phone, None, error="Eitaa API unreachable")


async def check_bale(phone: str) -> AccountInfo:
    """
    Bale Bot API (https://tapi.bale.ai) does not expose a membership-check
    endpoint either.
    """
    if not settings.bale_token:
        return AccountInfo("bale", phone, None, error="Bale token not configured")
    url = f"https://tapi.bale.ai/bot{settings.bale_token}/getMe"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return AccountInfo("bale", phone, None, error="Bale does not expose account-check endpoint")
    except Exception as exc:
        logger.exception("Bale check failed for %s", phone)
        return AccountInfo("bale", phone, None, error=str(exc))
    return AccountInfo("bale", phone, None, error="Bale API unreachable")


async def check_whatsapp(phone: str) -> AccountInfo:
    return AccountInfo(
        "whatsapp",
        phone,
        None,
        error="WhatsApp does not provide a public account-check API",
    )


async def check_rubika(phone: str) -> AccountInfo:
    return AccountInfo(
        "rubika",
        phone,
        None,
        error="Rubika does not provide a public account-check API",
    )


_CHECKERS = {
    "telegram": check_telegram,
    "eitaa": check_eitaa,
    "bale": check_bale,
    "whatsapp": check_whatsapp,
    "rubika": check_rubika,
}


async def check_all_platforms(phone: str) -> list[AccountInfo]:
    """Run all platform checkers concurrently and return results."""
    tasks = [checker(phone) for checker in _CHECKERS.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    out = []
    for platform, result in zip(_CHECKERS.keys(), results):
        if isinstance(result, Exception):
            out.append(AccountInfo(platform, phone, None, error=str(result)))
        else:
            out.append(result)
    return out


async def check_platform(phone: str, platform: str) -> AccountInfo:
    checker = _CHECKERS.get(platform)
    if not checker:
        return AccountInfo(platform, phone, None, error=f"Unknown platform: {platform}")
    return await checker(phone)
