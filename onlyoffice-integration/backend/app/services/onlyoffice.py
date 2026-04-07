from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import time
import uuid

from jose import jwt

from app.core.config import settings


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def generate_onlyoffice_token(payload: dict) -> str:
    """Sign an ONLYOFFICE editor config payload with the shared JWT secret."""
    return jwt.encode(payload, settings.onlyoffice_jwt_secret, algorithm="HS256")


def build_editor_config(
    *,
    document_key: str,
    document_title: str,
    document_url: str,
    callback_url: str,
    user_id: str,
    user_name: str,
    file_type: str = "docx",
    mode: str = "edit",
    lang: str = "fa",
) -> dict:
    """
    Build the full ONLYOFFICE editor configuration object.

    Returns a dict ready to be serialised into the page's ``DocsAPI.DocEditor`` call.
    The top-level ``token`` field is the JWT-signed version of the entire config
    so that ONLYOFFICE Document Server can verify it.
    """
    doc_type = _doc_type_from_extension(file_type)

    config: dict = {
        "document": {
            "fileType": file_type,
            "key": document_key,
            "title": document_title,
            "url": document_url,
            "permissions": {
                "comment": True,
                "download": True,
                "edit": mode == "edit",
                "print": True,
                "review": True,
            },
        },
        "documentType": doc_type,
        "editorConfig": {
            "callbackUrl": callback_url,
            "lang": lang,
            "mode": mode,
            "user": {
                "id": user_id,
                "name": user_name,
            },
            "customization": {
                "autosave": True,
                "chat": False,
                "comments": True,
                "compactHeader": False,
                "feedback": False,
                "forcesave": False,
                "help": False,
                "logo": {
                    "image": "",
                    "url": "",
                },
                "macros": False,
                "macrosMode": "disable",
                "plugins": False,
                "toolbarNoTabs": True,
            },
        },
    }

    config["token"] = generate_onlyoffice_token(config)
    return config


def _doc_type_from_extension(ext: str) -> str:
    """Map a file extension to an ONLYOFFICE documentType string."""
    ext = ext.lower().lstrip(".")
    _word = {"doc", "docx", "odt", "rtf", "txt", "html", "htm"}
    _cell = {"xls", "xlsx", "ods", "csv"}
    _slide = {"ppt", "pptx", "odp"}
    if ext in _word:
        return "word"
    if ext in _cell:
        return "cell"
    if ext in _slide:
        return "slide"
    return "word"


def new_document_key(doc_id: str, version: int = 1) -> str:
    """
    Generate a unique ONLYOFFICE document key.

    The key must change every time the document content changes so that
    ONLYOFFICE knows to reload the file from storage.
    """
    raw = f"{doc_id}:{version}:{time.time()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def verify_onlyoffice_callback_token(token: str) -> dict:
    """Decode and verify the JWT token sent by ONLYOFFICE in its callback."""
    from jose import JWTError

    try:
        return jwt.decode(
            token,
            settings.onlyoffice_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise ValueError("invalid_onlyoffice_token") from exc
