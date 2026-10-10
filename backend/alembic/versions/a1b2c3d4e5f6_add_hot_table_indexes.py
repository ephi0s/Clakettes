"""add hot table indexes

Revision ID: a1b2c3d4e5f6
Revises: f6a2b3c4d5e6
Create Date: 2026-08-31 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f6a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # These indexes were already created by c4a91d2e8f31, so plain
    # op.create_index() fails on any database that upgraded through it.
    _INDEXES = [
        ("ix_messages_sender_id", "messages", ["sender_id"]),
        ("ix_messages_receiver_id", "messages", ["receiver_id"]),
        ("ix_messages_group_id", "messages", ["group_id"]),
        ("ix_festivals_name", "festivals", ["name"]),
        ("ix_festivals_description", "festivals", ["description"]),
        ("ix_users_username", "users", ["username"]),
        ("ix_users_full_name", "users", ["full_name"]),
    ]
    existing = _existing_indexes()
    for name, table, columns in _INDEXES:
        if name in existing:
            continue
        op.create_index(name, table, columns, unique=False)


def _existing_indexes() -> set[str]:
    """Return the index names already present, per table, in the target database."""
    inspector = sa.inspect(op.get_bind())
    found: set[str] = set()
    for table in inspector.get_table_names():
        found.update(index["name"] for index in inspector.get_indexes(table))
    return found


def downgrade() -> None:
    """No-op: ``upgrade`` is idempotent and creates nothing on a linear history.

    Every index listed in ``_INDEXES`` is already created by the ancestor
    ``c4a91d2e8f31``, so ``upgrade`` skips them all and this revision owns no
    schema. Dropping them here as well would make ``c4a91d2e8f31`` fail with
    ``no such index`` when unwinding the chain, so removal is left to that
    revision.
    """
