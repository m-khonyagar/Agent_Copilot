"""
Campaign scheduler service.

Spreads a campaign's messages over time to respect per-platform daily rate
limits.  Uses APScheduler's AsyncIOScheduler backed by an in-memory job
store (sufficient for a single-process deployment; swap for a persistent
job store in production).

Flow:
  1. create_campaign_schedule()  – called when a campaign is started;
     creates one SendSchedule row per recipient with a staggered send time.
  2. run_pending_sends()  – called by a periodic tick (every minute); picks
     up all SendSchedule rows whose scheduled_at has passed, sends the
     message, and marks the row sent/failed.
"""

from __future__ import annotations

import asyncio
import logging
import math
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.database import (
    Campaign,
    CampaignRecipient,
    Contact,
    Message,
    MessageStatus,
    Notification,
    Platform,
    SendSchedule,
)
from app.services.message_sender import send_message

logger = logging.getLogger(__name__)
settings = get_settings()

_DAILY_LIMITS: dict[str, int] = {
    Platform.TELEGRAM: settings.telegram_daily_limit,
    Platform.EITAA: settings.eitaa_daily_limit,
    Platform.BALE: settings.bale_daily_limit,
    Platform.RUBIKA: settings.rubika_daily_limit,
    Platform.WHATSAPP: settings.whatsapp_daily_limit,
}


def _interval_seconds(platform: str, rate_limit_per_day: Optional[int]) -> float:
    """Return the minimum seconds between sends to stay within the daily limit."""
    limit = rate_limit_per_day or _DAILY_LIMITS.get(platform, 50)
    return 86400.0 / limit


async def create_campaign_schedule(db: AsyncSession, campaign: Campaign) -> int:
    """
    Generate SendSchedule rows for every recipient in *campaign*.
    Returns the number of rows created.
    """
    result = await db.execute(
        select(CampaignRecipient).where(CampaignRecipient.campaign_id == campaign.id)
    )
    recipients = result.scalars().all()

    interval = _interval_seconds(campaign.platform, campaign.rate_limit_per_day)
    start = campaign.scheduled_at or datetime.now(timezone.utc)

    rows = []
    for i, recipient in enumerate(recipients):
        send_at = start + timedelta(seconds=interval * i)
        rows.append(
            SendSchedule(
                campaign_id=campaign.id,
                contact_id=recipient.contact_id,
                platform=campaign.platform,
                scheduled_at=send_at,
                status="pending",
            )
        )

    db.add_all(rows)
    await db.commit()
    logger.info("Created %d send-schedule rows for campaign %d", len(rows), campaign.id)
    return len(rows)


async def run_pending_sends(db: AsyncSession) -> None:
    """Process all SendSchedule rows that are due and have not been sent yet."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(SendSchedule)
        .where(SendSchedule.status == "pending")
        .where(SendSchedule.scheduled_at <= now)
    )
    pending = result.scalars().all()

    for schedule in pending:
        contact_result = await db.execute(select(Contact).where(Contact.id == schedule.contact_id))
        contact = contact_result.scalar_one_or_none()
        if not contact:
            schedule.status = "failed"
            await db.commit()
            continue

        campaign_result = await db.execute(select(Campaign).where(Campaign.id == schedule.campaign_id))
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            schedule.status = "failed"
            await db.commit()
            continue

        recipient = contact.phone
        result = await send_message(schedule.platform, recipient, campaign.content)

        msg = Message(
            contact_id=contact.id,
            platform=schedule.platform,
            direction="outbound",
            content=campaign.content,
            campaign_id=campaign.id,
            status=MessageStatus.SENT if result.success else MessageStatus.FAILED,
            platform_message_id=result.platform_message_id,
            sent_at=datetime.now(timezone.utc) if result.success else None,
        )
        db.add(msg)

        schedule.status = "sent" if result.success else "failed"
        schedule.sent_at = datetime.now(timezone.utc)

        if result.success:
            campaign.sent_count = (campaign.sent_count or 0) + 1
        else:
            campaign.failed_count = (campaign.failed_count or 0) + 1

        notification = Notification(
            title=f"Message {'sent' if result.success else 'failed'} — {contact.name}",
            body=(
                f"Message to {contact.name} ({contact.phone}) via {schedule.platform} "
                + ("sent successfully." if result.success else f"failed: {result.error}")
            ),
            related_contact_id=contact.id,
        )
        db.add(notification)

        await db.commit()

    all_sent = await db.execute(
        select(SendSchedule)
        .where(SendSchedule.campaign_id.in_([s.campaign_id for s in pending]))
        .where(SendSchedule.status == "pending")
    )
    # Mark campaigns as completed when no more pending rows exist
    if not all_sent.scalars().first() and pending:
        campaign_ids = {s.campaign_id for s in pending}
        for cid in campaign_ids:
            c_res = await db.execute(select(Campaign).where(Campaign.id == cid))
            camp = c_res.scalar_one_or_none()
            if camp and camp.status == "running":
                camp.status = "completed"
                camp.completed_at = datetime.now(timezone.utc)
        await db.commit()
