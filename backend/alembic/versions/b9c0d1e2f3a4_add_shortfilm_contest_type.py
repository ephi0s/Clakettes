"""add shortfilm contest type and required festival

Revision ID: b9c0d1e2f3a4
Revises: c1d2e3f4a5b6
Create Date: 2026-11-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b9c0d1e2f3a4"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("shortfilms") as batch_op:
        batch_op.add_column(
            sa.Column(
                "contest_type",
                sa.String(length=30),
                nullable=False,
                server_default="official_section",
            )
        )
        batch_op.alter_column("festival_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_index("ix_shortfilms_contest_type", ["contest_type"], unique=False)
        batch_op.create_index("ix_shortfilms_festival_id", ["festival_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("shortfilms") as batch_op:
        batch_op.drop_index("ix_shortfilms_festival_id")
        batch_op.drop_index("ix_shortfilms_contest_type")
        batch_op.alter_column("festival_id", existing_type=sa.Integer(), nullable=True)
        batch_op.drop_column("contest_type")
