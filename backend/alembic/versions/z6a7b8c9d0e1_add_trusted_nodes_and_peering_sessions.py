"""add trusted_nodes and node_peering_sessions (Fase 2 - peering mTLS)

Revision ID: z6a7b8c9d0e1
Revises: c8d9e0f1a2b3
Create Date: 2026-11-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "z6a7b8c9d0e1"
down_revision: Union[str, None] = "c8d9e0f1a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trusted_nodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("node_domain", sa.String(length=255), nullable=False),
        sa.Column("cert_fingerprint_sha256", sa.String(length=64), nullable=False),
        sa.Column("cert_subject_cn", sa.String(length=255), nullable=True),
        sa.Column("cert_sans", mysql.JSON(), nullable=True),
        sa.Column("issuer_ca", sa.String(length=255), nullable=True),
        sa.Column("not_before", sa.DateTime(), nullable=True),
        sa.Column("not_after", sa.DateTime(), nullable=True),
        sa.Column("allowed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("consent_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("minimize_data", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("capabilities", mysql.JSON(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_trusted_nodes_cert_fingerprint_sha256"),
        "trusted_nodes",
        ["cert_fingerprint_sha256"],
        unique=True,
    )
    op.create_index(op.f("ix_trusted_nodes_node_domain"), "trusted_nodes", ["node_domain"], unique=True)
    op.create_index("ix_trusted_nodes_domain_allowed", "trusted_nodes", ["node_domain", "allowed"], unique=False)

    op.create_table(
        "node_peering_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("remote_domain", sa.String(length=255), nullable=True),
        sa.Column("remote_ip", sa.String(length=45), nullable=True),
        sa.Column("cert_fingerprint", sa.String(length=64), nullable=True),
        sa.Column("validated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["trusted_nodes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_node_peering_sessions_node_id"), "node_peering_sessions", ["node_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_node_peering_sessions_node_id"), table_name="node_peering_sessions")
    op.drop_table("node_peering_sessions")
    op.drop_index("ix_trusted_nodes_domain_allowed", table_name="trusted_nodes")
    op.drop_index(op.f("ix_trusted_nodes_node_domain"), table_name="trusted_nodes")
    op.drop_index(op.f("ix_trusted_nodes_cert_fingerprint_sha256"), table_name="trusted_nodes")
    op.drop_table("trusted_nodes")
