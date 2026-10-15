"""Router modules re-exported for convenience."""

from app.routers import festivals
from app.routers import users
from app.routers import shortfilms
from app.routers import chat
from app.routers import auth
from app.routers import auth_sessions
from app.routers import user_festival
from app.routers import uploads
from app.routers import search
from app.routers import admin
from app.routers import notifications
from app.routers import roles
from app.routers import participant_tags
from app.routers import user_roles
from app.routers import user_aliases
from app.routers import validation_rules
from app.routers import registration_forms
from app.routers import role_groups
from app.routers import committees
from app.routers import delegations
from app.routers import events
from app.routers import channels
from app.routers import keys
from app.routers import locations
from app.routers import location_tags
from app.routers import location_images
from app.routers import location_relations
from app.routers import shortfilm_locations
from app.routers import form_definitions
from app.routers import posts
from app.routers import badges

__all__ = [
    "festivals",
    "users",
    "shortfilms",
    "chat",
    "auth",
    "auth_sessions",
    "user_festival",
    "uploads",
    "search",
    "admin",
    "notifications",
    "roles",
    "participant_tags",
    "user_roles",
    "user_aliases",
    "validation_rules",
    "registration_forms",
    "role_groups",
    "committees",
    "delegations",
    "events",
    "channels",
    "keys",
    "locations",
    "location_tags",
    "location_images",
    "location_relations",
    "shortfilm_locations",
    "form_definitions",
    "posts",
    "badges",
]
