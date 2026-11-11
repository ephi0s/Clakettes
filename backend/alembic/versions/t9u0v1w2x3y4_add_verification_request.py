"""add verification request fields to user participant tags

Revision ID: t9u0v1w2x3y4
Revises: s8t9u0v1w2x3
Create Date: 2026-11-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "t9u0v1w2x3y4"
down_revision: Union[str, None] = "s8t9u0v1w2x3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_participant_tags", sa.Column("verification_document_url", sa.String(length=500), nullable=True))
    op.add_column("user_participant_tags", sa.Column("verification_requested_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_participant_tags", "verification_requested_at")
    op.drop_column("user_participant_tags", "verification_document_url")
