from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import (
    Campaign,
    Contact,
    Message,
    MessageStatus,
    Notification,
    PlatformAccount,
    SendSchedule,
)
from app.services.message_sender import send_message

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_contacts: int
    total_messages_sent: int
    total_messages_read: int
    total_inbound: int
    active_campaigns: int
    unread_notifications: int


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    is_read: bool
    created_at: datetime
    related_message_id: Optional[int]
    related_contact_id: Optional[int]

    class Config:
        from_attributes = True


class AdminReplyRequest(BaseModel):
    message_id: int  # the inbound message we are replying to
    content: str


class MessageThreadOut(BaseModel):
    contact_id: int
    contact_name: str
    contact_phone: str
    messages: list


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(db: AsyncSession = Depends(get_db)):
    total_contacts = (await db.execute(select(func.count(Contact.id)))).scalar_one()
    total_sent = (
        await db.execute(
            select(func.count(Message.id)).where(
                Message.direction == "outbound",
                Message.status.in_([MessageStatus.SENT, MessageStatus.DELIVERED, MessageStatus.READ]),
            )
        )
    ).scalar_one()
    total_read = (
        await db.execute(
            select(func.count(Message.id)).where(Message.status == MessageStatus.READ)
        )
    ).scalar_one()
    total_inbound = (
        await db.execute(
            select(func.count(Message.id)).where(Message.direction == "inbound")
        )
    ).scalar_one()
    active_campaigns = (
        await db.execute(
            select(func.count(Campaign.id)).where(Campaign.status.in_(["running", "scheduled"]))
        )
    ).scalar_one()
    unread_notifs = (
        await db.execute(
            select(func.count(Notification.id)).where(Notification.is_read == False)
        )
    ).scalar_one()

    return DashboardStats(
        total_contacts=total_contacts,
        total_messages_sent=total_sent,
        total_messages_read=total_read,
        total_inbound=total_inbound,
        active_campaigns=active_campaigns,
        unread_notifications=unread_notifs,
    )


@router.get("/notifications", response_model=List[NotificationOut])
async def list_notifications(unread_only: bool = False, db: AsyncSession = Depends(get_db)):
    q = select(Notification).order_by(desc(Notification.created_at))
    if unread_only:
        q = q.where(Notification.is_read == False)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/notifications/{notif_id}/read", response_model=NotificationOut)
async def mark_notification_read(notif_id: int, db: AsyncSession = Depends(get_db)):
    notif = await db.get(Notification, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif


@router.post("/notifications/read-all")
async def mark_all_notifications_read(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.is_read == False))
    for n in result.scalars().all():
        n.is_read = True
    await db.commit()
    return {"status": "ok"}


@router.get("/inbox", response_model=List[dict])
async def inbox(db: AsyncSession = Depends(get_db)):
    """Return all inbound messages grouped by contact for the admin to review and reply."""
    result = await db.execute(
        select(Message)
        .where(Message.direction == "inbound")
        .order_by(desc(Message.created_at))
    )
    messages = result.scalars().all()
    out = []
    for msg in messages:
        contact = await db.get(Contact, msg.contact_id)
        out.append(
            {
                "id": msg.id,
                "contact_id": msg.contact_id,
                "contact_name": contact.name if contact else "Unknown",
                "contact_phone": contact.phone if contact else "",
                "platform": msg.platform,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "status": msg.status,
            }
        )
    return out


@router.post("/reply", response_model=dict)
async def admin_reply(data: AdminReplyRequest, db: AsyncSession = Depends(get_db)):
    """
    Send a reply from the admin panel.

    The reply is dispatched via the *original* platform used to communicate
    with this contact.
    """
    original = await db.get(Message, data.message_id)
    if not original:
        raise HTTPException(status_code=404, detail="Original message not found")

    contact = await db.get(Contact, original.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    result = await send_message(original.platform, contact.phone, data.content)

    reply_msg = Message(
        contact_id=contact.id,
        platform=original.platform,
        direction="outbound",
        content=data.content,
        status=MessageStatus.SENT if result.success else MessageStatus.FAILED,
        platform_message_id=result.platform_message_id,
        sent_at=datetime.now(timezone.utc) if result.success else None,
    )
    db.add(reply_msg)
    await db.commit()
    await db.refresh(reply_msg)

    return {
        "success": result.success,
        "message_id": reply_msg.id,
        "error": result.error,
    }


@router.get("/history/{contact_id}", response_model=List[dict])
async def contact_history(contact_id: int, db: AsyncSession = Depends(get_db)):
    """Full message history for a specific contact (both inbound and outbound)."""
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    result = await db.execute(
        select(Message)
        .where(Message.contact_id == contact_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id,
            "direction": m.direction,
            "platform": m.platform,
            "content": m.content,
            "status": m.status,
            "sent_at": m.sent_at.isoformat() if m.sent_at else None,
            "read_at": m.read_at.isoformat() if m.read_at else None,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
