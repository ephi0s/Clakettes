"""add eligibility criteria and recipient verification to awards

Revision ID: r8s9t0u1v2w3
Revises: q7r8s9t0u1v2
Create Date: 2026-10-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "r8s9t0u1v2w3"
down_revision: Union[str, None] = "q7r8s9t0u1v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("awards", sa.Column("eligibility_criteria", sa.Text(), nullable=True))
    op.add_column(
        "awards",
        sa.Column("recipient_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("awards", sa.Column("recipient_verified_by", sa.Integer(), nullable=True))
    op.add_column("awards", sa.Column("recipient_verified_at", sa.DateTime(), nullable=True))
    op.add_column("awards", sa.Column("recipient_verification_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("awards", "recipient_verification_notes")
    op.drop_column("awards", "recipient_verified_at")
    op.drop_column("awards", "recipient_verified_by")
    op.drop_column("awards", "recipient_verified")
    op.drop_column("awards", "eligibility_criteria")
