"""create badges tables (profile insignias)

Revision ID: n4o5p6q7r8s9
Revises: m3n4o5p6q7r8
Create Date: 2026-10-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "n4o5p6q7r8s9"
down_revision: Union[str, None] = "m3n4o5p6q7r8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "badges",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("scope", sa.String(length=20), nullable=True),
        sa.Column("category", sa.String(length=30), nullable=True),
        sa.Column("festival_id", sa.Integer(), nullable=True),
        sa.Column("conditions", sa.JSON(), nullable=True),
        sa.Column("require_conditions", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["festival_id"], ["festivals.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_badges_festival_id", "badges", ["festival_id"], unique=False)
    op.create_index("ix_badges_name", "badges", ["name"], unique=True)
    op.create_index("ix_badges_id", "badges", ["id"], unique=False)
    op.create_table(
        "badge_assignments",
        sa.Column("badge_id", sa.Integer(), nullable=False),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("target_festival_id", sa.Integer(), nullable=True),
        sa.Column("granted_by", sa.Integer(), nullable=False),
        sa.Column("grant_festival_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["badge_id"], ["badges.id"]),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["target_festival_id"], ["festivals.id"]),
        sa.ForeignKeyConstraint(["granted_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["grant_festival_id"], ["festivals.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_badge_assignments_badge_id", "badge_assignments", ["badge_id"], unique=False)
    op.create_index("ix_badge_assignments_target_user_id", "badge_assignments", ["target_user_id"], unique=False)
    op.create_index(
        "ix_badge_assignments_target_festival_id", "badge_assignments", ["target_festival_id"], unique=False
    )
    op.create_index("ix_badge_assignments_id", "badge_assignments", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_badge_assignments_id", table_name="badge_assignments")
    op.drop_index("ix_badge_assignments_target_festival_id", table_name="badge_assignments")
    op.drop_index("ix_badge_assignments_target_user_id", table_name="badge_assignments")
    op.drop_index("ix_badge_assignments_badge_id", table_name="badge_assignments")
    op.drop_table("badge_assignments")
    op.drop_index("ix_badges_id", table_name="badges")
    op.drop_index("ix_badges_name", table_name="badges")
    op.drop_index("ix_badges_festival_id", table_name="badges")
    op.drop_table("badges")
