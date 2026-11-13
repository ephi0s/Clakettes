"""add node_policies table for federation allowlist/blocklist

Revision ID: v1w2x3y4z5a6
Revises: u0v1w2x3y4z5
Create Date: 2026-11-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "v1w2x3y4z5a6"
down_revision: Union[str, None] = "u0v1w2x3y4z5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "node_policies",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("node_domain", sa.String(255), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("node_domain", name="uq_node_policy_domain"),
    )
    op.create_index("ix_node_policies_node_domain", "node_policies", ["node_domain"])


def downgrade() -> None:
    op.drop_index("ix_node_policies_node_domain", table_name="node_policies")
    op.drop_table("node_policies")
