"""add moderation_reports table for federated report propagation

Revision ID: w2x3y4z5a6b7
Revises: v1w2x3y4z5a6
Create Date: 2026-11-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "w2x3y4z5a6b7"
down_revision: Union[str, None] = "v1w2x3y4z5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "moderation_reports",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("reporter_node", sa.String(255), nullable=False),
        sa.Column("target_node", sa.String(255), nullable=False),
        sa.Column("target_user_ref", sa.String(255), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_moderation_reports_reporter_node", "moderation_reports", ["reporter_node"])
    op.create_index("ix_moderation_reports_target_node", "moderation_reports", ["target_node"])


def downgrade() -> None:
    op.drop_index("ix_moderation_reports_target_node", table_name="moderation_reports")
    op.drop_index("ix_moderation_reports_reporter_node", table_name="moderation_reports")
    op.drop_table("moderation_reports")
