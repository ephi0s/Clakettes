"""add payment fields for registrations

Revision ID: f6a2b3c4d5e6
Revises: e5f1a2b3c4d5
Create Date: 2026-08-15 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a2b3c4d5e6"
down_revision: Union[str, None] = "e5f1a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("registration_forms", sa.Column("fee_amount", sa.Float(), nullable=True))
    op.add_column(
        "registration_forms", sa.Column("currency", sa.String(length=3), server_default="EUR", nullable=False)
    )
    op.add_column(
        "festival_registrations",
        sa.Column("payment_status", sa.String(length=20), server_default="unpaid", nullable=False),
    )
    op.add_column("festival_registrations", sa.Column("paid_at", sa.DateTime(), nullable=True))
    op.add_column("festival_registrations", sa.Column("payment_method", sa.String(length=50), nullable=True))
    op.add_column("festival_registrations", sa.Column("transaction_id", sa.String(length=100), nullable=True))
    op.create_index(
        op.f("ix_festival_registrations_payment_status"), "festival_registrations", ["payment_status"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_festival_registrations_payment_status"), table_name="festival_registrations")
    op.drop_column("festival_registrations", "transaction_id")
    op.drop_column("festival_registrations", "payment_method")
    op.drop_column("festival_registrations", "paid_at")
    op.drop_column("festival_registrations", "payment_status")
    op.drop_column("registration_forms", "currency")
    op.drop_column("registration_forms", "fee_amount")
