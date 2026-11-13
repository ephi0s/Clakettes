"""add jury_votes table (Fase 5)

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2
Create Date: 2026-11-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jury_votes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("festival_id", sa.Integer(), sa.ForeignKey("festivals.id"), nullable=False),
        sa.Column("juror_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("shortfilm_id", sa.Integer(), sa.ForeignKey("shortfilms.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("comment", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("jury_votes")
