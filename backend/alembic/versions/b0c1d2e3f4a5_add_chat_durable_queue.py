"""add_chat_durable_queue

Revision ID: b0c1d2e3f4a5
Revises: a9b0c1d2e3f4
Create Date: 2026-11-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "b0c1d2e3f4a5"
down_revision = "a9b0c1d2e3f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_outbox",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.String(length=36), nullable=False),
        sa.Column("node_origin", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_outbox_message_id", "chat_outbox", ["message_id"], unique=True)
    op.create_index("ix_chat_outbox_node_origin", "chat_outbox", ["node_origin"], unique=False)
    op.create_index("ix_chat_outbox_subject", "chat_outbox", ["subject"], unique=False)
    op.create_index("ix_chat_outbox_status", "chat_outbox", ["status"], unique=False)
    op.create_index("ix_chat_outbox_created_at", "chat_outbox", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chat_outbox_created_at", table_name="chat_outbox")
    op.drop_index("ix_chat_outbox_status", table_name="chat_outbox")
    op.drop_index("ix_chat_outbox_subject", table_name="chat_outbox")
    op.drop_index("ix_chat_outbox_node_origin", table_name="chat_outbox")
    op.drop_index("ix_chat_outbox_message_id", table_name="chat_outbox")
    op.drop_table("chat_outbox")
