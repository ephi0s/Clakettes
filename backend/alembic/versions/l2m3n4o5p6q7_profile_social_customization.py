"""profile social customization: banner/tagline/social_links

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-10-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "l2m3n4o5p6q7"
down_revision: Union[str, None] = "k1l2m3n4o5p6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("banner_url", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("tagline", sa.String(length=200), nullable=True))
    op.add_column("users", sa.Column("social_links", sa.JSON(), nullable=True))
    op.add_column("festivals", sa.Column("banner_url", sa.String(length=500), nullable=True))
    op.add_column("festivals", sa.Column("tagline", sa.String(length=200), nullable=True))
    op.add_column("festivals", sa.Column("social_links", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("festivals", "social_links")
    op.drop_column("festivals", "tagline")
    op.drop_column("festivals", "banner_url")
    op.drop_column("users", "social_links")
    op.drop_column("users", "tagline")
    op.drop_column("users", "banner_url")
