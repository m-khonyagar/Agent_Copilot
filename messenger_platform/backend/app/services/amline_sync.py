"""
Amline API integration service.

Provides two capabilities:
  1. Contact sync — pulls users from the Amline backend (`GET /admin/users`)
     and upserts them into the local Contact table so the messenger can reach
     Amline's client base directly.

  2. Message logging — pushes every sent/received message back to Amline's
     call-and-text log API (`POST /users/user-texts`) so the Amline CRM
     keeps a unified conversation history.

All network calls are async and fail gracefully: a connectivity error with
Amline never crashes the messenger or blocks a message send.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.database import Contact

logger = logging.getLogger(__name__)
settings = get_settings()


def _amline_headers() -> dict:
    """Build HTTP headers for Amline API calls."""
    headers: dict = {"Content-Type": "application/json"}
    if settings.amline_admin_token:
        headers["Authorization"] = f"Bearer {settings.amline_admin_token}"
    return headers


# ── OTP-based authentication helpers ─────────────────────────────────────────

async def amline_send_otp(mobile: str) -> dict:
    """
    Request an OTP from the Amline backend for the given mobile number.
    Returns the raw JSON response.
    """
    url = f"{settings.amline_base_url}/admin/otp/send"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json={"mobile": mobile})
            return resp.json()
    except Exception as exc:
        logger.warning("amline_send_otp failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def amline_verify_otp(mobile: str, otp: str) -> dict:
    """
    Verify an OTP with Amline and, on success, return an access token.
    Calls POST /admin/login which returns {access_token, refresh_token, user}.
    """
    url = f"{settings.amline_base_url}/admin/login"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json={"mobile": mobile, "otp": otp})
            return resp.json()
    except Exception as exc:
        logger.warning("amline_verify_otp failed: %s", exc)
        return {"error": str(exc)}


# ── Contact sync ──────────────────────────────────────────────────────────────

async def sync_contacts_from_amline(db: AsyncSession, page: int = 1, limit: int = 100) -> int:
    """
    Fetch one page of Amline users and upsert them as local Contacts.
    Only users that have a mobile number are imported.
    Returns the number of contacts created or updated.
    """
    if not settings.amline_admin_token:
        logger.info("AMLINE_ADMIN_TOKEN not set — skipping contact sync")
        return 0

    url = f"{settings.amline_base_url}/admin/users"
    params = {"page": page, "limit": limit}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=_amline_headers(), params=params)
            if resp.status_code != 200:
                logger.warning("Amline /admin/users returned %s", resp.status_code)
                return 0
            data = resp.json()
    except Exception as exc:
        logger.warning("sync_contacts_from_amline network error: %s", exc)
        return 0

    users = data.get("items", data if isinstance(data, list) else [])
    upserted = 0

    for user in users:
        mobile: Optional[str] = user.get("mobile") or user.get("phone")
        if not mobile:
            continue

        full_name: str = user.get("full_name") or user.get("name") or mobile
        amline_id: str = str(user.get("id", ""))
        notes = f"Amline user id: {amline_id}" if amline_id else None

        result = await db.execute(select(Contact).where(Contact.phone == mobile))
        contact = result.scalar_one_or_none()

        if contact is None:
            contact = Contact(name=full_name, phone=mobile, notes=notes)
            db.add(contact)
        else:
            contact.name = full_name
            if notes and not contact.notes:
                contact.notes = notes
            contact.updated_at = datetime.now(timezone.utc)

        upserted += 1

    await db.commit()
    logger.info("Amline contact sync: %d contacts upserted (page %d)", upserted, page)
    return upserted


# ── Message logging ───────────────────────────────────────────────────────────

async def log_message_to_amline(
    amline_user_id: str,
    direction: str,  # "outbound" | "inbound"
    platform: str,
    text: str,
) -> bool:
    """
    Push a single message event to Amline's user-texts log.
    Mapping:
      outbound → direction "sent"   (the messenger sent to the Amline client)
      inbound  → direction "incoming" (the Amline client replied)

    Returns True on success, False on any error.
    """
    if not settings.amline_admin_token or not amline_user_id:
        return False

    url = f"{settings.amline_base_url}/users/user-texts"
    amline_direction = "sent" if direction == "outbound" else "incoming"
    payload = {
        "user_id": amline_user_id,
        "type": amline_direction,
        "text": f"[{platform.upper()}] {text}",
        "direction": amline_direction,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=_amline_headers(), json=payload)
            if resp.status_code in (200, 201):
                return True
            logger.warning(
                "log_message_to_amline: unexpected status %s — %s",
                resp.status_code,
                resp.text[:200],
            )
            return False
    except Exception as exc:
        logger.warning("log_message_to_amline network error: %s", exc)
        return False


def extract_amline_user_id(notes: Optional[str]) -> Optional[str]:
    """
    Parse the Amline user id stored in a Contact's notes field.
    Notes are stored as "Amline user id: <id>" by sync_contacts_from_amline.
    """
    if not notes:
        return None
    prefix = "Amline user id: "
    for part in notes.split(";"):
        part = part.strip()
        if part.startswith(prefix):
            return part[len(prefix):].strip()
    return None
