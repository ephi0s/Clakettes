"""add verification fields to user participant tags

Revision ID: q7r8s9t0u1v2
Revises: p6q7r8s9t0u1
Create Date: 2026-10-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "q7r8s9t0u1v2"
down_revision: Union[str, None] = "p6q7r8s9t0u1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_participant_tags",
        sa.Column("verification_status", sa.String(length=50), nullable=False, server_default="unverified"),
    )
    op.add_column("user_participant_tags", sa.Column("verification_method", sa.String(length=50), nullable=True))
    op.add_column("user_participant_tags", sa.Column("verification_notes", sa.Text(), nullable=True))
    op.add_column("user_participant_tags", sa.Column("verified_by", sa.Integer(), nullable=True))
    op.add_column("user_participant_tags", sa.Column("verified_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_participant_tags", "verified_at")
    op.drop_column("user_participant_tags", "verified_by")
    op.drop_column("user_participant_tags", "verification_notes")
    op.drop_column("user_participant_tags", "verification_method")
    op.drop_column("user_participant_tags", "verification_status")
