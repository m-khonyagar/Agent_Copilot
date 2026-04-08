"""Add office_documents table

Revision ID: 20240407_office_docs
Revises: (set this to the last migration ID in your project)
Create Date: 2024-04-07
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20240407_office_docs"
down_revision = None  # ← Replace with the last existing migration ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "office_documents",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("file_type", sa.String(length=16), nullable=False, server_default="docx"),
        sa.Column("s3_key", sa.String(length=512), nullable=True),
        sa.Column("doc_key", sa.String(length=64), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_office_documents_owner_id"),
        "office_documents",
        ["owner_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_office_documents_owner_id"), table_name="office_documents"
    )
    op.drop_table("office_documents")
