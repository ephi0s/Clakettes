"""add event screenings and payments tables

Revision ID: g7h8i9j0k1l2
Revises: f9a0b1c2d3e4
Create Date: 2026-10-09 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "f9a0b1c2d3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_screenings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("shortfilm_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shortfilm_id"], ["shortfilms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_screenings_event_id", "event_screenings", ["event_id"])
    op.create_index("ix_event_screenings_shortfilm_id", "event_screenings", ["shortfilm_id"])
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("registration_id", sa.Integer(), nullable=True),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("provider_ref", sa.String(length=100), nullable=True),
        sa.Column("checkout_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["registration_id"], ["festival_registrations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_registration_id", "payments", ["registration_id"])
    op.create_index("ix_payments_event_id", "payments", ["event_id"])
    op.create_index("ix_payments_provider", "payments", ["provider"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_provider_ref", "payments", ["provider_ref"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_payments_provider_ref", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_provider", table_name="payments")
    op.drop_index("ix_payments_event_id", table_name="payments")
    op.drop_index("ix_payments_registration_id", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_event_screenings_shortfilm_id", table_name="event_screenings")
    op.drop_index("ix_event_screenings_event_id", table_name="event_screenings")
    op.drop_table("event_screenings")
