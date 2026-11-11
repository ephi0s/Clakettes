"""add jury notes, minutes and annotations to event screenings

Revision ID: s8t9u0v1w2x3
Revises: r8s9t0u1v2w3
Create Date: 2026-10-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "s8t9u0v1w2x3"
down_revision: Union[str, None] = "r8s9t0u1v2w3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("event_screenings", sa.Column("jury_notes", sa.Text(), nullable=True))
    op.add_column("event_screenings", sa.Column("minutes", sa.Text(), nullable=True))
    op.add_column("event_screenings", sa.Column("annotation", sa.String(length=50), nullable=True))
    op.add_column("event_screenings", sa.Column("annotated_by", sa.Integer(), nullable=True))
    op.add_column("event_screenings", sa.Column("annotated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("event_screenings", "annotated_at")
    op.drop_column("event_screenings", "annotated_by")
    op.drop_column("event_screenings", "annotation")
    op.drop_column("event_screenings", "minutes")
    op.drop_column("event_screenings", "jury_notes")
