"""add handle column to users for federated identity

Revision ID: z5a6b7c8d9e0
Revises: y4z5a6b7c8d9
Create Date: 2026-11-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "z5a6b7c8d9e0"
down_revision: Union[str, None] = "y4z5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("handle", sa.String(255), nullable=True))
    op.create_index("ix_users_handle", "users", ["handle"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_handle", table_name="users")
    op.drop_column("users", "handle")
