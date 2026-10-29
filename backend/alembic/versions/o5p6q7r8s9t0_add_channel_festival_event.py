"""add festival_id and event_id to channels

Revision ID: o5p6q7r8s9t0
Revises: n4o5p6q7r8s9
Create Date: 2026-10-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "o5p6q7r8s9t0"
down_revision: Union[str, None] = "n4o5p6q7r8s9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("channels", sa.Column("festival_id", sa.Integer(), nullable=True))
    op.add_column("channels", sa.Column("event_id", sa.Integer(), nullable=True))
    op.create_index("ix_channels_festival_id", "channels", ["festival_id"], unique=False)
    op.create_index("ix_channels_event_id", "channels", ["event_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_channels_event_id", table_name="channels")
    op.drop_index("ix_channels_festival_id", table_name="channels")
    op.drop_column("channels", "event_id")
    op.drop_column("channels", "festival_id")