"""add import_only/disable_chat/disable_search to node_policies

Revision ID: b7c8d9e0f1a2
Revises: a6b7c8d9e0f1
Create Date: 2026-11-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "a6b7c8d9e0f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("node_policies", sa.Column("import_only", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("node_policies", sa.Column("disable_chat", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("node_policies", sa.Column("disable_search", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("node_policies", "disable_search")
    op.drop_column("node_policies", "disable_chat")
    op.drop_column("node_policies", "import_only")
