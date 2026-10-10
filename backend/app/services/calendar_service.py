"""Calendar service — the shared agenda that spans every visible festival.

Visibility is resolved in a single SQL query (rather than per-event Python
checks) so that date-range limits and counts stay consistent:

- the global ``calendar.enabled`` setting hides the agenda entirely;
- ``Festival.show_in_calendar`` decides which festivals contribute events;
- ``Event.visibility_scope`` decides who inside that audience sees the event.

Anonymous visitors only ever see ``public`` events. Authenticated users also
get events addressed to the festivals they belong to, the roles they hold in
that festival, and the events they are registered for.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.enums import EventVisibilityScope, UserRoleStatus
from app.models.event import Event, EventAttendee, event_visibility_roles
from app.models.festival import Festival
from app.models.user import User
from app.models.user_festival import user_festival
from app.models.user_role import UserRole
from app.schemas.calendar import (
    AgendaEventResponse,
    AgendaFestivalResponse,
    AgendaResponse,
    CalendarFestivalVisibility,
    CalendarSettingsResponse,
)
from .app_setting_service import AppSettingService

_PRIVATE_SCOPES = (
    EventVisibilityScope.FESTIVAL_MEMBERS.value,
    EventVisibilityScope.ROLES.value,
    EventVisibilityScope.ATTENDEES_ONLY.value,
)

_ACTIVE_ROLE_STATUSES = [UserRoleStatus.ACTIVE.value, UserRoleStatus.APPROVED.value]


class CalendarService:
    """Builds the shared agenda and manages its visibility settings."""

    def __init__(self):
        self.settings_service = AppSettingService()

    # ------------------------------------------------------------------
    # Agenda
    # ------------------------------------------------------------------

    def get_agenda(
        self,
        db: Session,
        user: User | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        festival_ids: list[int] | None = None,
        event_type: str | None = None,
        limit: int = 200,
    ) -> AgendaResponse:
        """Return the agenda visible to *user* (None means anonymous)."""
        if not self.settings_service.is_calendar_enabled(db):
            return AgendaResponse(enabled=False, festivals=[], events=[], total=0)

        festivals = (
            db.query(Festival)
            .filter(Festival.is_active.is_(True), Festival.show_in_calendar.is_(True))
            .order_by(Festival.name)
            .all()
        )
        if festival_ids:
            allowed = set(festival_ids)
            festivals = [f for f in festivals if f.id in allowed]
        if not festivals:
            return AgendaResponse(enabled=True, festivals=[], events=[], total=0)

        query = self.visible_events_query(db, user, festival_ids)
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if date_from is not None:
            query = query.filter(func.coalesce(Event.end_date, Event.start_date) >= date_from)
        if date_to is not None:
            query = query.filter(Event.start_date <= date_to)

        events = query.order_by(Event.start_date, Event.sort_order, Event.id).limit(limit).all()
        names = {f.id: f for f in festivals}
        by_festival: dict[int, int] = {}

        payload: list[AgendaEventResponse] = []
        for event in events:
            festival = names.get(event.festival_id)
            if festival is None:
                continue
            by_festival[event.festival_id] = by_festival.get(event.festival_id, 0) + 1
            payload.append(self._to_agenda_event(event, festival))

        return AgendaResponse(
            enabled=True,
            festivals=[
                AgendaFestivalResponse(
                    id=f.id,
                    name=f.name,
                    logo_url=f.logo_url,
                    location=f.location,
                    event_count=by_festival.get(f.id, 0),
                )
                for f in festivals
            ],
            events=payload,
            total=len(payload),
        )

    def _visibility_clause(self, db: Session, user: User | None):
        """SQL predicate restricting events to those *user* may see."""
        if user is None:
            return Event.visibility_scope == EventVisibilityScope.PUBLIC.value

        clauses = [Event.visibility_scope == EventVisibilityScope.PUBLIC.value]

        member_festival_ids = select(user_festival.c.festival_id).where(user_festival.c.user_id == user.id)
        clauses.append(
            (Event.visibility_scope == EventVisibilityScope.FESTIVAL_MEMBERS.value)
            & Event.festival_id.in_(member_festival_ids)
        )

        attendee_event_ids = select(EventAttendee.event_id).where(
            EventAttendee.user_id == user.id,
            EventAttendee.is_hidden.is_(False),
        )
        clauses.append(
            (Event.visibility_scope == EventVisibilityScope.ATTENDEES_ONLY.value) & Event.id.in_(attendee_event_ids)
        )

        # The role must be held in the event's *own* festival, or be global.
        # An aliased Event keeps this subquery from auto-correlating with the
        # outer events table.
        event_for_roles = aliased(Event)
        role_event_ids = (
            select(event_visibility_roles.c.event_id)
            .join(event_for_roles, event_for_roles.id == event_visibility_roles.c.event_id)
            .join(UserRole, UserRole.role_id == event_visibility_roles.c.role_id)
            .where(
                UserRole.user_id == user.id,
                UserRole.status.in_(_ACTIVE_ROLE_STATUSES),
                (UserRole.festival_id == event_for_roles.festival_id) | (UserRole.festival_id.is_(None)),
            )
        )
        clauses.append((Event.visibility_scope == EventVisibilityScope.ROLES.value) & Event.id.in_(role_event_ids))

        return or_(*clauses)

    def visible_events_query(self, db: Session, user: User | None, festival_ids: list[int] | None = None):
        """Base Query[Event] of active events in calendar-enabled festivals that `user` may see."""
        if not self.settings_service.is_calendar_enabled(db):
            return db.query(Event).filter(False)
        festivals = (
            db.query(Festival)
            .filter(Festival.is_active.is_(True), Festival.show_in_calendar.is_(True))
            .order_by(Festival.name)
            .all()
        )
        if festival_ids:
            allowed = set(festival_ids)
            festivals = [f for f in festivals if f.id in allowed]
        if not festivals:
            return db.query(Event).filter(False)

        visible_ids = [f.id for f in festivals]
        query = db.query(Event).filter(
            Event.festival_id.in_(visible_ids),
            Event.is_active.is_(True),
            self._visibility_clause(db, user),
        )
        return query

    def _to_agenda_event(self, event: Event, festival: Festival) -> AgendaEventResponse:
        return AgendaEventResponse(
            id=event.id,
            festival_id=festival.id,
            festival_name=festival.name,
            title=event.title,
            description=event.description,
            short_description=event.short_description,
            event_type=event.event_type,
            start_date=event.start_date,
            end_date=event.end_date,
            location=event.location,
            venue=event.venue,
            venue_latitude=event.venue_latitude,
            venue_longitude=event.venue_longitude,
            image_url=event.image_url,
            color=event.color,
            capacity=event.capacity,
            is_active=bool(event.is_active),
            visibility_scope=event.visibility_scope or EventVisibilityScope.PUBLIC.value,
            is_private=(event.visibility_scope or EventVisibilityScope.PUBLIC.value) in _PRIVATE_SCOPES,
            updated_at=event.updated_at,
        )

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def get_settings(self, db: Session) -> CalendarSettingsResponse:
        """Return the admin-facing calendar configuration."""
        festivals = db.query(Festival).order_by(Festival.name).all()
        counts = dict(
            db.query(Event.festival_id, func.count(Event.id))
            .filter(Event.is_active.is_(True))
            .group_by(Event.festival_id)
            .all()
        )
        return CalendarSettingsResponse(
            calendar_enabled=self.settings_service.is_calendar_enabled(db),
            festivals=[
                CalendarFestivalVisibility(
                    id=f.id,
                    name=f.name,
                    logo_url=f.logo_url,
                    location=f.location,
                    is_active=bool(f.is_active),
                    show_in_calendar=bool(f.show_in_calendar),
                    event_count=counts.get(f.id, 0),
                )
                for f in festivals
            ],
        )

    def update_settings(
        self,
        db: Session,
        calendar_enabled: bool | None = None,
        festival_ids: list[int] | None = None,
    ) -> CalendarSettingsResponse:
        """Apply admin changes and return the refreshed configuration.

        Passing ``festival_ids`` marks exactly those festivals as visible and
        hides the rest. Passing ``None`` leaves the per-festival flags alone.
        """
        if calendar_enabled is not None:
            self.settings_service.set_value(
                db,
                "calendar.enabled",
                calendar_enabled,
                description="Show the shared agenda across all festivals",
            )
        if festival_ids is not None:
            wanted = set(festival_ids)
            for festival in db.query(Festival).all():
                flag = festival.id in wanted
                if bool(festival.show_in_calendar) != flag:
                    festival.show_in_calendar = flag
            db.commit()
        return self.get_settings(db)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_ics(self, agenda: AgendaResponse) -> str:
        """Render the agenda as an ICS calendar string."""
        from .export_service import _ics_text, _utc_format, ics_calendar_body

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Clakettes//Agenda//ES",
            "X-WR-CALNAME:Clakettes",
        ]
        stamp = _utc_format(datetime.now(timezone.utc))
        for event in agenda.events:
            start = event.start_date
            end = event.end_date or (start + timedelta(hours=1))
            if end <= start:
                end = start + timedelta(hours=1)
            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:event-{event.id}@clakettes")
            lines.append(f"DTSTAMP:{stamp}")
            lines.append(f"DTSTART:{_utc_format(start)}")
            lines.append(f"DTEND:{_utc_format(end)}")
            lines.append(f"SUMMARY:{_ics_text(event.title)}")
            location = event.venue or event.location
            if location:
                lines.append(f"LOCATION:{_ics_text(location)}")
            if event.short_description or event.description:
                lines.append(f"DESCRIPTION:{_ics_text(event.short_description or event.description)}")
            lines.append(f"CATEGORIES:{_ics_text(event.event_type)}")
            lines.append(f"X-APPLE-STRUCTURE-LOCATION:{_ics_text(event.festival_name)}")
            lines.append("END:VEVENT")
        lines.append("END:VCALENDAR")
        return ics_calendar_body(lines)
