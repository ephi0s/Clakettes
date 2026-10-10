"""add user dav token

Revision ID: c5d4e3f2a1b0
Revises: b2c3d4e5f6a7
Create Date: 2026-10-02 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c5d4e3f2a1b0"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("dav_token_hash", sa.String(length=64), nullable=True),
    )
    op.create_index(op.f("ix_users_dav_token_hash"), "users", ["dav_token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_dav_token_hash"), table_name="users")
    op.drop_column("users", "dav_token_hash")
