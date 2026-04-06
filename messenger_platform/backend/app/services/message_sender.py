"""
Message sender service.

Handles sending a single message on a given platform and updating the
message record with the platform's message-id (needed later to poll for
read receipts).

Each platform section is guarded by a credentials check so the service
degrades gracefully when tokens are not configured.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SendResult:
    def __init__(self, success: bool, platform_message_id: Optional[str] = None, error: Optional[str] = None):
        self.success = success
        self.platform_message_id = platform_message_id
        self.error = error


async def send_telegram(phone: str, text: str) -> SendResult:
    """Send a message via Telegram using Telethon (user account, not bot)."""
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        return SendResult(False, error="Telegram API credentials not configured")
    try:
        from telethon import TelegramClient

        client = TelegramClient("messenger_session", settings.telegram_api_id, settings.telegram_api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return SendResult(False, error="Telegram session not authorised")
        msg = await client.send_message(phone, text)
        await client.disconnect()
        return SendResult(True, platform_message_id=str(msg.id))
    except Exception as exc:
        logger.exception("Telegram send failed to %s", phone)
        return SendResult(False, error=str(exc))


async def send_telegram_bot(chat_id: str, text: str) -> SendResult:
    """Send a message via Telegram Bot API."""
    if not settings.telegram_bot_token:
        return SendResult(False, error="Telegram bot token not configured")
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text})
            data = resp.json()
            if data.get("ok"):
                msg_id = str(data["result"]["message_id"])
                return SendResult(True, platform_message_id=msg_id)
            return SendResult(False, error=data.get("description", "Unknown error"))
    except Exception as exc:
        logger.exception("Telegram bot send failed to %s", chat_id)
        return SendResult(False, error=str(exc))


async def send_eitaa_bot(chat_id: str, text: str) -> SendResult:
    """Send a message via Eitaa Bot API."""
    if not settings.eitaa_token:
        return SendResult(False, error="Eitaa token not configured")
    url = f"https://eitaa.com/BotAPI/bot{settings.eitaa_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text})
            data = resp.json()
            if data.get("ok"):
                msg_id = str(data["result"]["message_id"])
                return SendResult(True, platform_message_id=msg_id)
            return SendResult(False, error=data.get("description", "Unknown error"))
    except Exception as exc:
        logger.exception("Eitaa bot send failed to %s", chat_id)
        return SendResult(False, error=str(exc))


async def send_bale_bot(chat_id: str, text: str) -> SendResult:
    """Send a message via Bale Bot API."""
    if not settings.bale_token:
        return SendResult(False, error="Bale token not configured")
    url = f"https://tapi.bale.ai/bot{settings.bale_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text})
            data = resp.json()
            if data.get("ok"):
                msg_id = str(data["result"]["message_id"])
                return SendResult(True, platform_message_id=msg_id)
            return SendResult(False, error=data.get("description", "Unknown error"))
    except Exception as exc:
        logger.exception("Bale bot send failed to %s", chat_id)
        return SendResult(False, error=str(exc))


async def send_message(platform: str, recipient: str, text: str) -> SendResult:
    """Dispatch a single message to the correct platform sender."""
    platform = platform.lower()
    if platform == "telegram":
        return await send_telegram(recipient, text)
    elif platform == "telegram_bot":
        return await send_telegram_bot(recipient, text)
    elif platform == "eitaa":
        return await send_eitaa_bot(recipient, text)
    elif platform == "bale":
        return await send_bale_bot(recipient, text)
    else:
        return SendResult(False, error=f"Platform '{platform}' send not implemented")
