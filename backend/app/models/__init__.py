"""Convenience imports for all SQLAlchemy models."""

from app.models.base import BaseModel
from app.models.festival import Festival
from app.models.user import User
from app.models.shortfilm import ShortFilm
from app.models.message import Message
from app.models.user_festival import user_festival
from app.models.notification import Notification
from app.models.role import Role, FestivalRole, RoleScope, RoleDependency, RoleConflict
from app.models.role_group import RoleGroup, RoleGroupMembership
from app.models.participant_tag import ParticipantTag, FestivalParticipantTag, ParticipantTagCategory
from app.models.user_role import UserRole, UserParticipantTag, UserRoleStatus, UserRoleVisibility
from app.models.user_alias import UserAlias, AliasContext, AliasVisibility
from app.models.committee import Committee, CommitteeMember
from app.models.role_delegation import RoleDelegation
from app.models.role_transition import RoleTransition
from app.models.registration import (
    RegistrationForm,
    RegistrationFormSection,
    RegistrationFormSectionRole,
    RegistrationFormSectionTag,
    RegistrationFormLink,
    FestivalRegistration,
    RegistrationSectionSelection,
    RegistrationStatus,
)
from app.models.event import (
    Event,
    EventTicketType,
    EventSeat,
    EventReservation,
    EventAttendee,
    EventType,
    EventVisibilityScope,
    SeatStatus,
    AttendeeStatus,
    event_visibility_roles,
)
from app.models.event_screening import EventScreening
from app.models.payment import Payment
from app.models.award import Award
from app.models.festival_rulebook import FestivalRulebook
from app.models.user_session import UserSession
from app.models.validation_rule import (
    ValidationRule,
    ValidationRuleGroup,
    ValidationScope,
    FieldType,
    validation_rule_group_rules,
)
from app.models.group import Group, GroupMember
from app.models.channel import Channel, ChannelMember
from app.models.user_key import UserKey
from app.models.location import Location
from app.models.location_tag import LocationTag
from app.models.shortfilm_location import ShortFilmLocation
from app.models.location_image import LocationImage
from app.models.location_relation import LocationRelation
from app.models.festival_location import FestivalLocation
from app.models.app_setting import AppSetting
from app.models.form_definition import (
    FormDefinition,
    FormPage,
    FormField,
    FormFieldOption,
    FormResponse,
    FormFieldResponse,
    FormAccessRule,
    FormLink,
    FormType,
    FormFieldType,
    FormAccessLevel,
    SubmissionStatus,
)

__all__ = [
    "BaseModel",
    "Festival",
    "User",
    "ShortFilm",
    "Message",
    "user_festival",
    "Notification",
    "Role",
    "FestivalRole",
    "RoleScope",
    "RoleDependency",
    "RoleConflict",
    "RoleGroup",
    "RoleGroupMembership",
    "ParticipantTag",
    "FestivalParticipantTag",
    "ParticipantTagCategory",
    "UserRole",
    "UserParticipantTag",
    "UserRoleStatus",
    "UserRoleVisibility",
    "UserAlias",
    "AliasContext",
    "AliasVisibility",
    "Committee",
    "CommitteeMember",
    "RoleDelegation",
    "RoleTransition",
    "ValidationRule",
    "ValidationRuleGroup",
    "ValidationScope",
    "FieldType",
    "validation_rule_group_rules",
    "RegistrationForm",
    "RegistrationFormSection",
    "RegistrationFormSectionRole",
    "RegistrationFormSectionTag",
    "RegistrationFormLink",
    "FestivalRegistration",
    "RegistrationSectionSelection",
    "RegistrationStatus",
    "Event",
    "EventTicketType",
    "EventSeat",
    "EventReservation",
    "EventAttendee",
    "EventType",
    "EventVisibilityScope",
    "event_visibility_roles",
    "SeatStatus",
    "AttendeeStatus",
    "EventScreening",
    "Payment",
    "Award",
    "FestivalRulebook",
    "UserSession",
    "Group",
    "GroupMember",
    "Channel",
    "ChannelMember",
    "UserKey",
    "Location",
    "LocationTag",
    "ShortFilmLocation",
    "LocationImage",
    "LocationRelation",
    "FestivalLocation",
    "AppSetting",
    "FormDefinition",
    "FormPage",
    "FormField",
    "FormFieldOption",
    "FormResponse",
    "FormFieldResponse",
    "FormAccessRule",
    "FormLink",
    "FormType",
    "FormFieldType",
    "FormAccessLevel",
    "SubmissionStatus",
]
