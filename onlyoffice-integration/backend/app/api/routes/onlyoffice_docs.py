from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.ids import parse_uuid
from app.db.session import get_db
from app.models.office_document import OfficeDocument, OfficeDocumentStatus
from app.models.user import User
from app.services.onlyoffice import (
    build_editor_config,
    new_document_key,
    verify_onlyoffice_callback_token,
)
from app.services.s3 import get_s3_client

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Pydantic schemas ─────────────────────────────────────────────────────────


class OfficeDocumentOut(BaseModel):
    id: str
    title: str
    file_type: str
    status: str
    version: int
    owner_id: str
    created_at: str
    updated_at: str | None = None


class OfficeDocumentCreate(BaseModel):
    title: str
    file_type: str = "docx"


class EditorConfigOut(BaseModel):
    config: dict[str, Any]
    onlyoffice_url: str


class CallbackPayload(BaseModel):
    status: int
    key: str
    url: str | None = None
    users: list[str] | None = None


# ── Helpers ──────────────────────────────────────────────────────────────────


def _to_out(doc: OfficeDocument) -> OfficeDocumentOut:
    return OfficeDocumentOut(
        id=str(doc.id),
        title=doc.title,
        file_type=doc.file_type,
        status=doc.status,
        version=doc.version,
        owner_id=str(doc.owner_id),
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else None,
    )


def _s3_key_for_doc(doc_id: str, file_type: str) -> str:
    return f"office-docs/{doc_id}.{file_type}"


def _public_download_url(s3_key: str) -> str:
    """Build a pre-signed S3/MinIO URL valid for 1 hour."""
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": s3_key},
        ExpiresIn=3600,
    )


# ── Routes ───────────────────────────────────────────────────────────────────


@router.get("", response_model=list[OfficeDocumentOut])
def list_office_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all office documents owned by the current user."""
    docs = (
        db.query(OfficeDocument)
        .filter(OfficeDocument.owner_id == user.id)
        .order_by(OfficeDocument.created_at.desc())
        .all()
    )
    return [_to_out(d) for d in docs]


@router.post("", response_model=OfficeDocumentOut, status_code=201)
def create_office_document(
    body: OfficeDocumentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new (empty) office document record."""
    doc = OfficeDocument(
        owner_id=user.id,
        title=body.title,
        file_type=body.file_type,
        status=OfficeDocumentStatus.active.value,
        version=1,
    )
    db.add(doc)
    db.flush()

    # Generate the first document key and S3 key
    doc.s3_key = _s3_key_for_doc(str(doc.id), body.file_type)
    doc.doc_key = new_document_key(str(doc.id), version=1)

    db.commit()
    db.refresh(doc)
    return _to_out(doc)


@router.get("/{doc_id}", response_model=OfficeDocumentOut)
def get_office_document(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = _get_doc_or_404(doc_id, user, db)
    return _to_out(doc)


@router.delete("/{doc_id}", status_code=204)
def delete_office_document(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = _get_doc_or_404(doc_id, user, db)
    db.delete(doc)
    db.commit()


@router.get("/{doc_id}/editor-config", response_model=EditorConfigOut)
def get_editor_config(
    doc_id: str,
    mode: str = Query(default="edit", pattern="^(edit|view)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Return the ONLYOFFICE editor configuration for a document.

    The frontend embeds this config into the ``DocsAPI.DocEditor`` initialiser.
    """
    doc = _get_doc_or_404(doc_id, user, db)

    if not doc.s3_key:
        raise HTTPException(status_code=404, detail="document_has_no_content")

    document_url = _public_download_url(doc.s3_key)

    # The callback URL must be reachable by the ONLYOFFICE Document Server
    base_url = settings.onlyoffice_callback_base_url or str(request.base_url).rstrip("/")
    callback_url = f"{base_url}/onlyoffice-docs/{doc_id}/callback"

    config = build_editor_config(
        document_key=doc.doc_key or new_document_key(str(doc.id), doc.version),
        document_title=doc.title,
        document_url=document_url,
        callback_url=callback_url,
        user_id=str(user.id),
        user_name=user.name or user.mobile,
        file_type=doc.file_type,
        mode=mode,
    )

    return EditorConfigOut(
        config=config,
        onlyoffice_url=settings.onlyoffice_server_url,
    )


@router.post("/{doc_id}/upload-url")
def get_upload_url(
    doc_id: str,
    file_type: str = Query(default="docx"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a pre-signed PUT URL so the browser can upload the initial document directly to S3."""
    doc = _get_doc_or_404(doc_id, user, db)

    s3_key = _s3_key_for_doc(str(doc.id), file_type)
    client = get_s3_client()
    presigned_url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": s3_key,
            "ContentType": _content_type(file_type),
        },
        ExpiresIn=600,
    )

    doc.s3_key = s3_key
    doc.file_type = file_type
    doc.doc_key = new_document_key(str(doc.id), doc.version)
    db.commit()

    return {"upload_url": presigned_url, "s3_key": s3_key}


@router.post("/{doc_id}/callback")
async def onlyoffice_callback(
    doc_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Callback endpoint called by the ONLYOFFICE Document Server after a save.

    ONLYOFFICE statuses:
        0 — No document with the key identifier could be found.
        1 — Document is being edited.
        2 — Document is ready for saving.
        3 — Document saving error has occurred.
        4 — Document is closed with no changes.
        6 — Forcibly saved document.
        7 — Error has occurred while force saving the document.
    """
    # Verify JWT from Authorization header if JWT is enabled
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ")
        try:
            verify_onlyoffice_callback_token(token)
        except ValueError:
            return JSONResponse({"error": 1}, status_code=200)

    body: dict = await request.json()
    status: int = body.get("status", 0)
    download_url: str | None = body.get("url")

    try:
        doc_uuid = parse_uuid(doc_id)
    except ValueError:
        return JSONResponse({"error": 1}, status_code=200)

    doc = db.get(OfficeDocument, doc_uuid)
    if not doc:
        return JSONResponse({"error": 1}, status_code=200)

    # Status 2 or 6 → document is ready to be saved
    if status in (2, 6) and download_url:
        # Security: validate the callback download URL is from the expected ONLYOFFICE server
        if not _is_trusted_onlyoffice_url(download_url):
            logger.warning("Rejecting untrusted ONLYOFFICE callback URL: %s", download_url)
            return JSONResponse({"error": 1}, status_code=200)

        doc.status = OfficeDocumentStatus.saving.value
        db.commit()

        try:
            await _download_and_store(doc, download_url, db)
            doc.status = OfficeDocumentStatus.saved.value
            doc.version += 1
            doc.doc_key = new_document_key(str(doc.id), doc.version)
        except (httpx.HTTPError, Exception) as exc:
            logger.exception("Failed to save office document %s: %s", doc_id, exc)
            doc.status = OfficeDocumentStatus.error.value

        db.commit()

    elif status == 3:
        doc.status = OfficeDocumentStatus.error.value
        db.commit()

    # ONLYOFFICE expects {"error": 0} on success
    return JSONResponse({"error": 0}, status_code=200)


# ── Private helpers ──────────────────────────────────────────────────────────


def _get_doc_or_404(doc_id: str, user: User, db: Session) -> OfficeDocument:
    try:
        uid = parse_uuid(doc_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="invalid_document_id")

    doc = db.get(OfficeDocument, uid)
    if not doc:
        raise HTTPException(status_code=404, detail="document_not_found")
    if doc.owner_id != user.id:
        raise HTTPException(status_code=403, detail="forbidden")

    return doc


def _is_trusted_onlyoffice_url(url: str) -> bool:
    """
    Validate that a URL received in an ONLYOFFICE callback originates from the
    configured ONLYOFFICE Document Server, preventing SSRF attacks.
    """
    try:
        parsed_callback = urlparse(url)
        parsed_server = urlparse(settings.onlyoffice_server_url)
        return (
            parsed_callback.scheme in ("http", "https")
            and parsed_callback.netloc == parsed_server.netloc
        )
    except Exception:
        return False


async def _download_and_store(doc: OfficeDocument, url: str, db: Session) -> None:
    """
    Download the saved document from ONLYOFFICE and upload it to S3/MinIO.

    Note: `url` has already been validated by `_is_trusted_onlyoffice_url`
    before this function is called, ensuring it originates from the configured
    ONLYOFFICE Document Server (same hostname). This prevents SSRF attacks.
    """
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content

    s3 = get_s3_client()
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=doc.s3_key,
        Body=content,
        ContentType=_content_type(doc.file_type),
    )


def _content_type(file_type: str) -> str:
    mapping = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pdf": "application/pdf",
        "odt": "application/vnd.oasis.opendocument.text",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "odp": "application/vnd.oasis.opendocument.presentation",
    }
    return mapping.get(file_type.lower(), "application/octet-stream")
