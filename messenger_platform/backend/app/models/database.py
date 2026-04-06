from datetime import datetime, timezone

def _utcnow():
    return datetime.now(timezone.utc)
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Platform(str, PyEnum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    EITAA = "eitaa"
    BALE = "bale"
    RUBIKA = "rubika"


class MessageStatus(str, PyEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    platform_accounts = relationship("PlatformAccount", back_populates="contact", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="contact", cascade="all, delete-orphan")


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    has_account = Column(Boolean, nullable=True)
    username = Column(String(255), nullable=True)
    last_online = Column(DateTime, nullable=True)
    last_checked = Column(DateTime, nullable=True)

    contact = relationship("Contact", back_populates="platform_accounts")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    direction = Column(String(10), default="outbound")  # outbound | inbound
    content = Column(Text, nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING)
    platform_message_id = Column(String(255), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)

    contact = relationship("Contact", back_populates="messages")
    campaign = relationship("Campaign", back_populates="messages")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="draft")  # draft|scheduled|running|completed|failed
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    rate_limit_per_day = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    messages = relationship("Message", back_populates="campaign")
    recipients = relationship("CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan")


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)

    campaign = relationship("Campaign", back_populates="recipients")
    contact = relationship("Contact")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    related_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    related_contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)


class SendSchedule(Base):
    __tablename__ = "send_schedules"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")  # pending|sent|failed
