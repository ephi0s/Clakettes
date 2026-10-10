"""Shared enumerations used across models, schemas, and services."""

import enum


class RoleScope(enum.Enum):
    GLOBAL = "global"
    FESTIVAL = "festival"


class UserRoleStatus(enum.Enum):
    PROPOSED = "proposed"
    INVITED = "invited"
    UNDER_REVIEW = "under_review"
    PENDING = "pending"
    ACTIVE = "active"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class UserRoleVisibility(enum.Enum):
    PUBLIC = "public"
    FESTIVAL = "festival"
    HIDDEN = "hidden"
    PRIVATE = "private"


class AliasContext(enum.Enum):
    GLOBAL = "global"
    FESTIVAL = "festival"
    SHORTFILM = "shortfilm"
    CHAT = "chat"
    PUBLIC_PROFILE = "public_profile"
    CREDITS = "credits"


class AliasVisibility(enum.Enum):
    FESTIVAL_ONLY = "festival_only"
    ALL_ASSOCIATED = "all_associated"
    SELECTED = "selected"


class ParticipantTagCategory(enum.Enum):
    DIRECTION = "direction"
    ACTING = "acting"
    PRODUCTION = "production"
    CAMERA = "camera"
    SOUND = "sound"
    LIGHTING = "lighting"
    WRITING = "writing"
    EDITING = "editing"
    VFX = "vfx"
    ART = "art"
    COSTUME = "costume"
    MAKEUP = "makeup"
    PROPS = "props"
    MUSIC = "music"
    POST_PRODUCTION = "post_production"
    DISTRIBUTION = "distribution"
    OTHER = "other"


class FormType(enum.Enum):
    USER_CREATION = "user_creation"
    FESTIVAL_REGISTRATION = "festival_registration"
    INTERNAL = "internal"


class FormFieldType(enum.Enum):
    STRING = "string"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    DATE = "date"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    FILE = "file"
    ALIAS = "alias"
    ROLE_SELECTOR = "role_selector"
    TAG_SELECTOR = "tag_selector"
    SECTION_BREAK = "section_break"
    STATIC_TEXT = "static_text"


class FormAccessLevel(enum.Enum):
    VIEW = "view"
    SUBMIT = "submit"
    MANAGE = "manage"


class SubmissionStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class RegistrationStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"


class PaymentStatus(enum.Enum):
    UNPAID = "unpaid"
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class ValidationScope(enum.Enum):
    GLOBAL = "global"
    FESTIVAL = "festival"
    ROLE = "role"
    TAG = "tag"


class FieldType(enum.Enum):
    STRING = "string"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    DATE = "date"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"


class DelegationStatus(enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class EventType(enum.Enum):
    GALA = "gala"
    SCREENING = "screening"
    WORKSHOP = "workshop"
    PANEL = "panel"
    NETWORKING = "networking"
    AWARDS = "awards"
    PARTY = "party"
    MASTERCLASS = "masterclass"
    QANDA = "qanda"
    MEETING = "meeting"
    OTHER = "other"


class EventVisibilityScope(enum.Enum):
    """Who is allowed to see an event on the shared agenda.

    PUBLIC: anyone, authenticated or not.
    FESTIVAL_MEMBERS: only users linked to the event's festival.
    ROLES: only users holding one of the roles in ``event_visibility_roles``
        for that festival (or a global role).
    ATTENDEES_ONLY: only users registered as attendees of the event.
    """

    PUBLIC = "public"
    FESTIVAL_MEMBERS = "festival_members"
    ROLES = "roles"
    ATTENDEES_ONLY = "attendees_only"


class SeatStatus(enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    ASSIGNED = "assigned"
    BLOCKED = "blocked"


class AttendeeStatus(enum.Enum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"


class LocationBadge(enum.Enum):
    SUGGESTED = "suggested"
    MANDATORY = "mandatory"
    FEATURED = "featured"


class TagStatus(enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REVOKED = "revoked"


class FilmLocationRole(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BACKGROUND = "background"
    MENTIONED = "mentioned"


class FestivalRulebookCategory(enum.Enum):
    OFFICIAL_SECTION = "official_section"
    CONTEST = "contest"
    ACTIVITY = "activity"
    OTHER = "other"
