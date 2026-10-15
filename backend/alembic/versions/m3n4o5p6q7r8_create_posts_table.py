"""create posts table (profile microblogging wall)

Revision ID: m3n4o5p6q7r8
Revises: l2m3n4o5p6q7
Create Date: 2026-10-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "m3n4o5p6q7r8"
down_revision: Union[str, None] = "l2m3n4o5p6q7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("festival_id", sa.Integer(), nullable=True),
        sa.Column("parent_post_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embed_url", sa.String(length=1000), nullable=True),
        sa.Column("embed_type", sa.String(length=30), nullable=True),
        sa.Column("allow_replies", sa.Boolean(), nullable=True),
        sa.Column("is_pinned", sa.Boolean(), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["festival_id"], ["festivals.id"]),
        sa.ForeignKeyConstraint(["parent_post_id"], ["posts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_posts_author_id", "posts", ["author_id"], unique=False)
    op.create_index("ix_posts_target_user_id", "posts", ["target_user_id"], unique=False)
    op.create_index("ix_posts_festival_id", "posts", ["festival_id"], unique=False)
    op.create_index("ix_posts_parent_post_id", "posts", ["parent_post_id"], unique=False)
    op.create_index("ix_posts_id", "posts", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_posts_id", table_name="posts")
    op.drop_index("ix_posts_parent_post_id", table_name="posts")
    op.drop_index("ix_posts_festival_id", table_name="posts")
    op.drop_index("ix_posts_target_user_id", table_name="posts")
    op.drop_index("ix_posts_author_id", table_name="posts")
    op.drop_table("posts")
