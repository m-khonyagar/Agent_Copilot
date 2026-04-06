from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import (
    Campaign,
    CampaignRecipient,
    Contact,
    Message,
    MessageStatus,
    Notification,
    Platform,
)
from app.services.message_sender import send_message
from app.services.scheduler import create_campaign_schedule

router = APIRouter(prefix="/messages", tags=["messages"])

# ── WebSocket connection manager ─────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        for ws in list(self.active):
            try:
                await ws.send_json(data)
            except Exception:
                self.active.remove(ws)


manager = ConnectionManager()


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class SendSingleRequest(BaseModel):
    contact_id: int
    platform: str
    content: str


class CampaignCreate(BaseModel):
    name: str
    platform: str
    content: str
    contact_ids: List[int]
    scheduled_at: Optional[datetime] = None
    rate_limit_per_day: Optional[int] = None


class MessageOut(BaseModel):
    id: int
    contact_id: int
    platform: str
    direction: str
    content: str
    status: str
    platform_message_id: Optional[str]
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None

    class Config:
        from_attributes = True


class CampaignOut(BaseModel):
    id: int
    name: str
    platform: str
    content: str
    status: str
    total_recipients: int
    sent_count: int
    failed_count: int
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _enrich_message(msg: Message, db: AsyncSession) -> MessageOut:
    contact = await db.get(Contact, msg.contact_id)
    out = MessageOut.model_validate(msg)
    if contact:
        out.contact_name = contact.name
        out.contact_phone = contact.phone
    return out


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("", response_model=List[MessageOut])
async def list_messages(
    contact_id: Optional[int] = None,
    platform: Optional[str] = None,
    direction: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Message).order_by(desc(Message.created_at))
    if contact_id:
        q = q.where(Message.contact_id == contact_id)
    if platform:
        q = q.where(Message.platform == platform)
    if direction:
        q = q.where(Message.direction == direction)
    result = await db.execute(q)
    msgs = result.scalars().all()
    return [await _enrich_message(m, db) for m in msgs]


@router.post("/send", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_single(data: SendSingleRequest, db: AsyncSession = Depends(get_db)):
    """Send a single message to a contact on a specific platform."""
    contact = await db.get(Contact, data.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    msg = Message(
        contact_id=data.contact_id,
        platform=data.platform,
        direction="outbound",
        content=data.content,
        status=MessageStatus.PENDING,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    result = await send_message(data.platform, contact.phone, data.content)
    msg.status = MessageStatus.SENT if result.success else MessageStatus.FAILED
    msg.platform_message_id = result.platform_message_id
    msg.sent_at = datetime.now(timezone.utc) if result.success else None

    notif = Notification(
        title=f"Message {'sent' if result.success else 'failed'} to {contact.name}",
        body=(
            f"{'✓' if result.success else '✗'} {data.platform} → {contact.name} ({contact.phone})"
            + ("" if result.success else f": {result.error}")
        ),
        related_message_id=msg.id,
        related_contact_id=contact.id,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(msg)

    await manager.broadcast({"event": "message_sent", "message_id": msg.id, "status": msg.status})
    return await _enrich_message(msg, db)


@router.post("/campaigns", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    """Create a bulk-message campaign with optional scheduling and rate limiting."""
    # Validate contacts exist
    contacts = []
    for cid in data.contact_ids:
        c = await db.get(Contact, cid)
        if not c:
            raise HTTPException(status_code=404, detail=f"Contact {cid} not found")
        contacts.append(c)

    campaign = Campaign(
        name=data.name,
        platform=data.platform,
        content=data.content,
        status="scheduled" if data.scheduled_at else "running",
        total_recipients=len(data.contact_ids),
        sent_count=0,
        failed_count=0,
        scheduled_at=data.scheduled_at,
        started_at=datetime.now(timezone.utc) if not data.scheduled_at else None,
        rate_limit_per_day=data.rate_limit_per_day,
    )
    db.add(campaign)
    await db.flush()

    for cid in data.contact_ids:
        db.add(CampaignRecipient(campaign_id=campaign.id, contact_id=cid))

    await db.commit()
    await db.refresh(campaign)

    # Build the send schedule
    await create_campaign_schedule(db, campaign)

    return campaign


@router.get("/campaigns", response_model=List[CampaignOut])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).order_by(desc(Campaign.created_at)))
    return result.scalars().all()


@router.get("/campaigns/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    camp = await db.get(Campaign, campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return camp


@router.post("/{message_id}/mark-read", response_model=MessageOut)
async def mark_read(message_id: int, db: AsyncSession = Depends(get_db)):
    """Webhook-style endpoint: called when a platform confirms the message was read."""
    msg = await db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.status = MessageStatus.READ
    msg.read_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(msg)
    await manager.broadcast({"event": "message_read", "message_id": msg.id})
    return await _enrich_message(msg, db)


@router.post("/inbound", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def receive_inbound(
    contact_id: int,
    platform: str,
    content: str,
    platform_message_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Record an inbound reply from a user (called by platform webhooks or polling)."""
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    msg = Message(
        contact_id=contact_id,
        platform=platform,
        direction="inbound",
        content=content,
        status=MessageStatus.DELIVERED,
        platform_message_id=platform_message_id,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(msg)

    notif = Notification(
        title=f"New reply from {contact.name}",
        body=f"{contact.name} ({contact.phone}) replied via {platform}: {content[:80]}",
        related_message_id=None,
        related_contact_id=contact.id,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(msg)

    await manager.broadcast({"event": "inbound_message", "message_id": msg.id, "contact_id": contact_id})
    return await _enrich_message(msg, db)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket for real-time message status updates."""
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
