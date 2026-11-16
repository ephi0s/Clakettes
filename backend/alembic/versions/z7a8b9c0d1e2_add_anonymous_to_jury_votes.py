"""add anonymous to jury_votes (Fase 5 - votación del jurado)

Revision ID: z7a8b9c0d1e2
Revises: z6a7b8c9d0e1
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "z7a8b9c0d1e2"
down_revision: Union[str, None] = "z6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jury_votes",
        sa.Column("anonymous", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("jury_votes", "anonymous")
