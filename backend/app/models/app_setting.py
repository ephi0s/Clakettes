"""Key/value store for runtime settings toggled from the admin panel.

Settings are stored in the database (not in the environment) so a global admin
can change them at runtime through the API. Well-known keys are listed in
``app.services.app_setting_service``.
"""

from sqlalchemy import Column, String, JSON
from app.models.base import BaseModel


class AppSetting(BaseModel):
    """A single runtime setting.

    Attributes:
        key: Unique dotted identifier, e.g. ``calendar.enabled``.
        value: JSON-serialisable payload (bool, str, int, list...).
        value_type: Declared type used to coerce values read back.
        description: Human-readable explanation shown in the admin panel.
    """

    __tablename__ = "app_settings"

    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(JSON, nullable=True)
    value_type = Column(String(20), nullable=False, default="boolean")
    description = Column(String(300), nullable=True)

    def __repr__(self):
        return f"<AppSetting(key='{self.key}', value={self.value!r})>"
