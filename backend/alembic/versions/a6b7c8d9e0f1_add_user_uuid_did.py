"""add uuid and did columns to users for stable federated identity

Revision ID: a6b7c8d9e0f1
Revises: z5a6b7c8d9e0
Create Date: 2026-11-13
"""

import uuid as _uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6b7c8d9e0f1"
down_revision: Union[str, None] = "z5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("uuid", sa.String(36), nullable=True))
    op.add_column("users", sa.Column("did", sa.String(255), nullable=True))
    bind = op.get_bind()
    for row in bind.execute(sa.text("SELECT id FROM users")).fetchall():
        bind.execute(sa.text("UPDATE users SET uuid = :u WHERE id = :i"), {"u": str(_uuid.uuid4()), "i": row[0]})
    op.create_index("ix_users_uuid", "users", ["uuid"], unique=True)
    op.create_index("ix_users_did", "users", ["did"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_did", table_name="users")
    op.drop_index("ix_users_uuid", table_name="users")
    op.drop_column("users", "did")
    op.drop_column("users", "uuid")
