"""align schema with models

Resolves schema drift left by earlier revisions:

* ``b2c3d4e5f6a7`` created ``festivals.show_in_calendar`` as ``NOT NULL``, but the
  model declares it as a nullable ``Boolean`` with a Python-side ``default=True``.
* ``b2c3d4e5f6a7`` created ``ix_event_visibility_roles_role_id``, which the
  ``event_visibility_roles`` association table does not declare.
* ``c4a91d2e8f31`` created ``ix_users_username`` as non-unique, but the model
  declares ``users.username`` as ``unique=True``.

Revision ID: f9a0b1c2d3e4
Revises: c5d4e3f2a1b0
Create Date: 2026-10-06 09:00:00.000000

"""

from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa


revision: str = "f9a0b1c2d3e4"
down_revision: Union[str, None] = "c5d4e3f2a1b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DUPLICATE_USERNAMES_SQL = (
    "SELECT username, COUNT(*) AS occurrences, GROUP_CONCAT(id) AS user_ids "
    "FROM users GROUP BY username HAVING COUNT(*) > 1 ORDER BY username"
)

SHOW_IN_CALENDAR_BACKFILL_SQL = "UPDATE festivals SET show_in_calendar = 1 WHERE show_in_calendar IS NULL"


def _assert_usernames_unique() -> None:
    """Abort before any DDL if ``users.username`` currently holds duplicates.

    Creating the unique index would otherwise fail with a raw ``IntegrityError``
    that names neither the offending values nor a way out. Skipped in offline
    mode (``--sql``), where no connection is available to inspect.
    """
    if context.is_offline_mode():
        return

    duplicates = op.get_bind().execute(sa.text(DUPLICATE_USERNAMES_SQL)).fetchall()
    if not duplicates:
        return

    details = ", ".join(f"{row.username!r} x{row.occurrences} (user ids: {row.user_ids})" for row in duplicates)
    raise RuntimeError(
        f"Cannot create unique index 'ix_users_username': {len(duplicates)} duplicated username value(s) already "
        f"exist in 'users' -> {details}. The model requires users.username to be unique, so the migration stops "
        "here without changing anything. Resolve the duplicates (rename or merge the accounts, e.g. "
        "'UPDATE users SET username = :new_username WHERE id = :id') and re-run 'alembic upgrade head'."
    )


def _backfill_show_in_calendar() -> None:
    """Replace missing ``show_in_calendar`` values with 1 (visible) before relaxing the NOT NULL.

    The application treats a missing value as *visible*: ``Festival`` declares
    ``default=True``, ``FestivalCreate`` defaults to ``True``, and every query
    filters with ``Festival.show_in_calendar.is_(True)``, which excludes NULL.
    Writing NULL would therefore silently hide festivals from the shared agenda,
    so existing NULLs are normalised to 1 instead.
    """
    op.execute(sa.text(SHOW_IN_CALENDAR_BACKFILL_SQL))


def upgrade() -> None:
    _assert_usernames_unique()

    _backfill_show_in_calendar()
    with op.batch_alter_table("festivals") as batch_op:
        batch_op.alter_column(
            "show_in_calendar",
            existing_type=sa.Boolean(),
            existing_server_default=sa.true(),
            nullable=True,
        )

    op.drop_index(op.f("ix_event_visibility_roles_role_id"), table_name="event_visibility_roles")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.create_index(op.f("ix_event_visibility_roles_role_id"), "event_visibility_roles", ["role_id"], unique=False)

    _backfill_show_in_calendar()
    with op.batch_alter_table("festivals") as batch_op:
        batch_op.alter_column(
            "show_in_calendar",
            existing_type=sa.Boolean(),
            existing_server_default=sa.true(),
            nullable=False,
        )
