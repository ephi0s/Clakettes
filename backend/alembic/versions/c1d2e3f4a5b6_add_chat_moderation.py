"""add chat moderation tables

Revision ID: c1d2e3f4a5b6
Revises: b0c1d2e3f4a5
Create Date: 2026-11-20
"""

from alembic import op
import sqlalchemy as sa

revision = "c1d2e3f4a5b6"
down_revision = "b0c1d2e3f4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "message_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("reporter_id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"]),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_message_reports_id", "message_reports", ["id"], unique=False)
    op.create_index("ix_message_reports_reporter_id", "message_reports", ["reporter_id"], unique=False)
    op.create_index("ix_message_reports_message_id", "message_reports", ["message_id"], unique=False)
    op.create_index("ix_message_reports_status", "message_reports", ["status"], unique=False)
    op.create_table(
        "chat_mutes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.Column("node_domain", sa.String(length=255), nullable=True),
        sa.Column("until", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_mutes_id", "chat_mutes", ["id"], unique=False)
    op.create_index("ix_chat_mutes_user_id", "chat_mutes", ["user_id"], unique=False)
    op.create_index("ix_chat_mutes_channel_id", "chat_mutes", ["channel_id"], unique=False)
    op.create_index("ix_chat_mutes_node_domain", "chat_mutes", ["node_domain"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chat_mutes_node_domain", table_name="chat_mutes")
    op.drop_index("ix_chat_mutes_channel_id", table_name="chat_mutes")
    op.drop_index("ix_chat_mutes_user_id", table_name="chat_mutes")
    op.drop_index("ix_chat_mutes_id", table_name="chat_mutes")
    op.drop_table("chat_mutes")
    op.drop_index("ix_message_reports_status", table_name="message_reports")
    op.drop_index("ix_message_reports_message_id", table_name="message_reports")
    op.drop_index("ix_message_reports_reporter_id", table_name="message_reports")
    op.drop_index("ix_message_reports_id", table_name="message_reports")
    op.drop_table("message_reports")
