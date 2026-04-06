from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import Contact, Platform, PlatformAccount
from app.services.platform_checker import check_all_platforms, check_platform

router = APIRouter(prefix="/contacts", tags=["contacts"])


# ── Pydantic schemas ────────────────────────────────────────────────────────

class ContactCreate(BaseModel):
    name: str
    phone: str
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class PlatformAccountOut(BaseModel):
    platform: str
    has_account: Optional[bool]
    username: Optional[str]
    last_online: Optional[datetime]
    last_checked: Optional[datetime]

    class Config:
        from_attributes = True


class ContactOut(BaseModel):
    id: int
    name: str
    phone: str
    notes: Optional[str]
    created_at: datetime
    platform_accounts: List[PlatformAccountOut] = []

    class Config:
        from_attributes = True


# ── Routes ──────────────────────────────────────────────────────────────────

@router.get("", response_model=List[ContactOut])
async def list_contacts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact))
    contacts = result.scalars().all()
    # eagerly load platform_accounts
    out = []
    for c in contacts:
        pa_result = await db.execute(select(PlatformAccount).where(PlatformAccount.contact_id == c.id))
        c.platform_accounts = pa_result.scalars().all()
        out.append(c)
    return out


@router.post("", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
async def create_contact(data: ContactCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Contact).where(Contact.phone == data.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Phone number already exists")
    contact = Contact(name=data.name, phone=data.phone, notes=data.notes)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    contact.platform_accounts = []
    return contact


@router.get("/{contact_id}", response_model=ContactOut)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    pa_result = await db.execute(select(PlatformAccount).where(PlatformAccount.contact_id == contact_id))
    contact.platform_accounts = pa_result.scalars().all()
    return contact


@router.patch("/{contact_id}", response_model=ContactOut)
async def update_contact(contact_id: int, data: ContactUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    contact.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(contact)
    pa_result = await db.execute(select(PlatformAccount).where(PlatformAccount.contact_id == contact_id))
    contact.platform_accounts = pa_result.scalars().all()
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(contact)
    await db.commit()


@router.post("/{contact_id}/check-platforms", response_model=List[PlatformAccountOut])
async def check_contact_platforms(contact_id: int, db: AsyncSession = Depends(get_db)):
    """Check all platforms for a contact's phone number."""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    infos = await check_all_platforms(contact.phone)
    now = datetime.now(timezone.utc)
    out = []
    for info in infos:
        pa_result = await db.execute(
            select(PlatformAccount).where(
                PlatformAccount.contact_id == contact_id,
                PlatformAccount.platform == info.platform,
            )
        )
        pa = pa_result.scalar_one_or_none()
        if pa is None:
            pa = PlatformAccount(contact_id=contact_id, platform=info.platform)
            db.add(pa)
        pa.has_account = info.has_account
        pa.username = info.username
        pa.last_online = info.last_online
        pa.last_checked = now
        out.append(pa)

    await db.commit()
    return [
        PlatformAccountOut(
            platform=p.platform,
            has_account=p.has_account,
            username=p.username,
            last_online=p.last_online,
            last_checked=p.last_checked,
        )
        for p in out
    ]


@router.post("/{contact_id}/check-platform/{platform}", response_model=PlatformAccountOut)
async def check_single_platform(contact_id: int, platform: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    info = await check_platform(contact.phone, platform)
    now = datetime.now(timezone.utc)

    pa_result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.contact_id == contact_id,
            PlatformAccount.platform == platform,
        )
    )
    pa = pa_result.scalar_one_or_none()
    if pa is None:
        pa = PlatformAccount(contact_id=contact_id, platform=platform)
        db.add(pa)
    pa.has_account = info.has_account
    pa.username = info.username
    pa.last_online = info.last_online
    pa.last_checked = now
    await db.commit()

    return PlatformAccountOut(
        platform=pa.platform,
        has_account=pa.has_account,
        username=pa.username,
        last_online=pa.last_online,
        last_checked=pa.last_checked,
    )
