"""add unique constraint on event seat location

Revision ID: a8b9c0d1e2f3
Revises: z7a8b9c0d1e2
Create Date: 2026-11-20
"""

from typing import Sequence, Union

from alembic import op

revision: str = "a8b9c0d1e2f3"
down_revision: Union[str, None] = "z7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("event_seats") as batch_op:
        batch_op.create_unique_constraint(
            "uq_event_seat_location",
            ["event_id", "section", "row_label", "number"],
        )


def downgrade() -> None:
    with op.batch_alter_table("event_seats") as batch_op:
        batch_op.drop_constraint("uq_event_seat_location", type_="unique")
