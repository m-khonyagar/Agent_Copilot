from __future__ import annotations

import enum
import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPkMixin


class OfficeDocumentStatus(str, enum.Enum):
    active = "active"
    saving = "saving"
    saved = "saved"
    error = "error"


class OfficeDocument(UUIDPkMixin, TimestampMixin, Base):
    """Represents an editable office document managed via ONLYOFFICE."""

    __tablename__ = "office_documents"

    # Who owns/uploaded this document
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Human-readable title shown in the editor toolbar
    title: Mapped[str] = mapped_column(String(256))

    # File extension determines document type: docx, xlsx, pptx, …
    file_type: Mapped[str] = mapped_column(String(16), default="docx")

    # S3 / MinIO object key where the document bytes are stored
    s3_key: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # ONLYOFFICE document key — must change whenever file content changes
    doc_key: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Version counter incremented on every successful save callback
    version: Mapped[int] = mapped_column(Integer, default=1)

    # Lifecycle status
    status: Mapped[str] = mapped_column(
        String(16), default=OfficeDocumentStatus.active.value
    )
