"""AppSetting service — runtime settings toggled by a global admin.

SQLite stores a JSON scalar as text, so ``true`` comes back as the string
``"true"``. Every read goes through :func:`coerce` to normalise the value
according to the row's ``value_type`` before handing it to callers.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting

#: Well-known setting keys.
CALENDAR_ENABLED = "calendar.enabled"

#: Defaults applied when a key has no row yet.
DEFAULTS: dict[str, Any] = {
    CALENDAR_ENABLED: True,
}


def coerce(value: Any, value_type: str) -> Any:
    """Normalise *value* read from the database into *value_type*.

    SQLite returns JSON scalars as strings (``"true"``, ``"3"``), MariaDB
    returns them already typed, so both paths are handled here.
    """
    if value_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes", "on")
        return bool(value)
    if value_type == "integer":
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    if value_type == "string":
        return None if value is None else str(value)
    return value


class AppSettingService:
    """Reads and writes rows in the ``app_settings`` key/value table."""

    def get_row(self, db: Session, key: str) -> AppSetting | None:
        return db.query(AppSetting).filter(AppSetting.key == key).first()

    def get_value(self, db: Session, key: str, default: Any = None) -> Any:
        """Return the coerced value for *key*, or *default* when unset."""
        row = self.get_row(db, key)
        if row is None:
            return DEFAULTS.get(key, default)
        value = coerce(row.value, row.value_type)
        if value is None:
            return DEFAULTS.get(key, default)
        return value

    def set_value(self, db: Session, key: str, value: Any, description: str | None = None) -> AppSetting:
        """Insert or update *key*, coercing *value* to its declared type."""
        row = self.get_row(db, key)
        if row is None:
            row = AppSetting(key=key, value_type="boolean" if isinstance(value, bool) else "string")
            db.add(row)
        elif isinstance(value, bool):
            row.value_type = "boolean"
        row.value = value
        if description is not None:
            row.description = description
        db.commit()
        db.refresh(row)
        return row

    def is_calendar_enabled(self, db: Session) -> bool:
        """Return True when the global admin has the shared agenda enabled."""
        return bool(self.get_value(db, CALENDAR_ENABLED, True))
