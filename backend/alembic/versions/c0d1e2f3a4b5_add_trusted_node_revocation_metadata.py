"""add trusted node revocation metadata

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
Create Date: 2026-11-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c0d1e2f3a4b5"
down_revision: Union[str, None] = "b9c0d1e2f3a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("trusted_nodes") as batch_op:
        batch_op.add_column(sa.Column("revoked_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("revocation_reason", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("revoked_by", sa.String(length=255), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("trusted_nodes") as batch_op:
        batch_op.drop_column("revoked_by")
        batch_op.drop_column("revocation_reason")
        batch_op.drop_column("revoked_at")
