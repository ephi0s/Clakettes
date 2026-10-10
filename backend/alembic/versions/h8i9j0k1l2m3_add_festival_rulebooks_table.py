"""add festival rulebooks table

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-10-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "h8i9j0k1l2m3"
down_revision: Union[str, None] = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "festival_rulebooks",
        sa.Column("festival_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=True),
        sa.Column("external_url", sa.String(length=500), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["festival_id"], ["festivals.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_festival_rulebooks_id"), "festival_rulebooks", ["id"], unique=False)
    op.create_index(op.f("ix_festival_rulebooks_festival_id"), "festival_rulebooks", ["festival_id"], unique=False)
    op.create_index(op.f("ix_festival_rulebooks_event_id"), "festival_rulebooks", ["event_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_festival_rulebooks_event_id"), table_name="festival_rulebooks")
    op.drop_index(op.f("ix_festival_rulebooks_festival_id"), table_name="festival_rulebooks")
    op.drop_index(op.f("ix_festival_rulebooks_id"), table_name="festival_rulebooks")
    op.drop_table("festival_rulebooks")
