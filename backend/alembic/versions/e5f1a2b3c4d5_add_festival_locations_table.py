"""add festival_locations table

Revision ID: e5f1a2b3c4d5
Revises: c4a91d2e8f31
Create Date: 2026-08-02 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f1a2b3c4d5"
down_revision: Union[str, None] = "c4a91d2e8f31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "festival_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("festival_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["festival_id"], ["festivals.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("festival_id", "location_id", name="uq_festival_location"),
    )
    op.create_index(op.f("ix_festival_locations_id"), "festival_locations", ["id"])
    op.create_index(op.f("ix_festival_locations_festival_id"), "festival_locations", ["festival_id"])
    op.create_index(op.f("ix_festival_locations_location_id"), "festival_locations", ["location_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_festival_locations_location_id"), table_name="festival_locations")
    op.drop_index(op.f("ix_festival_locations_festival_id"), table_name="festival_locations")
    op.drop_index(op.f("ix_festival_locations_id"), table_name="festival_locations")
    op.drop_table("festival_locations")
