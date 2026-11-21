"""add identity_redirects and migration_audits (Fase 7 - portabilidad)

Revision ID: a9b0c1d2e3f4
Revises: a8b9c0d1e2f3
Create Date: 2026-11-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a9b0c1d2e3f4"
down_revision: Union[str, None] = "a8b9c0d1e2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identity_redirects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("old_ref", sa.String(length=255), nullable=False),
        sa.Column("new_ref", sa.String(length=255), nullable=False),
        sa.Column("target_domain", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_identity_redirects_old_ref"), "identity_redirects", ["old_ref"], unique=True)

    op.create_table(
        "migration_audits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("source_domain", sa.String(length=255), nullable=True),
        sa.Column("target_domain", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_migration_audits_entity_type"), "migration_audits", ["entity_type"], unique=False)
    op.create_index(op.f("ix_migration_audits_entity_id"), "migration_audits", ["entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_migration_audits_entity_id"), table_name="migration_audits")
    op.drop_index(op.f("ix_migration_audits_entity_type"), table_name="migration_audits")
    op.drop_table("migration_audits")
    op.drop_index(op.f("ix_identity_redirects_old_ref"), table_name="identity_redirects")
    op.drop_table("identity_redirects")
