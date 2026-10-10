"""add agenda visibility settings

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-02 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "festivals",
        sa.Column("show_in_calendar", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.add_column(
        "events",
        sa.Column(
            "visibility_scope",
            sa.String(length=30),
            server_default="public",
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_events_visibility_scope"), "events", ["visibility_scope"], unique=False)
    op.create_table(
        "event_visibility_roles",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id", "role_id"),
    )
    op.create_index(
        op.f("ix_event_visibility_roles_role_id"),
        "event_visibility_roles",
        ["role_id"],
        unique=False,
    )
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("value_type", sa.String(length=20), server_default="boolean", nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_app_settings_id"), "app_settings", ["id"], unique=False)
    op.create_index(op.f("ix_app_settings_key"), "app_settings", ["key"], unique=True)
    op.bulk_insert(
        sa.table(
            "app_settings",
            sa.column("key", sa.String),
            sa.column("value", sa.JSON),
            sa.column("value_type", sa.String),
            sa.column("description", sa.String),
        ),
        [
            {
                "key": "calendar.enabled",
                "value": True,
                "value_type": "boolean",
                "description": "Show the shared agenda across all festivals",
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("app_settings")
    op.drop_index(op.f("ix_event_visibility_roles_role_id"), table_name="event_visibility_roles")
    op.drop_table("event_visibility_roles")
    op.drop_index(op.f("ix_events_visibility_scope"), table_name="events")
    op.drop_column("events", "visibility_scope")
    op.drop_column("festivals", "show_in_calendar")
