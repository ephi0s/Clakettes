"""Convenience imports for all service classes."""

from app.services.festival_service import FestivalService
from app.services.user_service import UserService
from app.services.shortfilm_service import ShortFilmService
from app.services.message_service import MessageService
from app.services.role_service import RoleService, FestivalRoleService, UserRoleService
from app.services.participant_tag_service import (
    ParticipantTagService,
    FestivalParticipantTagService,
    UserParticipantTagService,
)
from app.services.user_alias_service import UserAliasService
from app.services.validation_rule_service import ValidationRuleService, ValidationRuleGroupService
from app.services.group_service import GroupService
from app.services.registration_service import (
    RegistrationFormService,
    RegistrationFormSectionService,
    RegistrationFormLinkService,
    FestivalRegistrationService,
)
from app.services.event_service import (
    EventService,
    EventTicketTypeService,
    EventSeatService,
    EventReservationService,
    EventAttendeeService,
)
from app.services.award_service import AwardService
from app.services.app_setting_service import AppSettingService
from app.services.calendar_service import CalendarService
from app.services.channel_service import ChannelService
from app.services.notification_service import NotificationService
from app.services.auth_session_service import AuthSessionService
from app.services.user_festival_service import UserFestivalService
from app.services.user_key_service import UserKeyService
from app.services.search_service import SearchService
from app.services.admin_service import AdminService
from app.services.location_service import LocationService
from app.services.location_tag_service import LocationTagService
from app.services.shortfilm_location_service import ShortFilmLocationService
from app.services.location_image_service import LocationImageService
from app.services.location_relation_service import LocationRelationService

__all__ = [
    "FestivalService",
    "UserService",
    "ShortFilmService",
    "MessageService",
    "RoleService",
    "FestivalRoleService",
    "UserRoleService",
    "ParticipantTagService",
    "FestivalParticipantTagService",
    "UserParticipantTagService",
    "UserAliasService",
    "ValidationRuleService",
    "ValidationRuleGroupService",
    "GroupService",
    "RegistrationFormService",
    "RegistrationFormSectionService",
    "RegistrationFormLinkService",
    "FestivalRegistrationService",
    "EventService",
    "EventTicketTypeService",
    "EventSeatService",
    "EventReservationService",
    "EventAttendeeService",
    "ChannelService",
    "NotificationService",
    "AuthSessionService",
    "UserFestivalService",
    "UserKeyService",
    "SearchService",
    "AdminService",
    "AwardService",
    "AppSettingService",
    "CalendarService",
    "LocationService",
    "LocationTagService",
    "ShortFilmLocationService",
    "LocationImageService",
    "LocationRelationService",
]
