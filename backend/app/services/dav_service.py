"""CalDAV service for read-only access to calendar collections."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dav import constants
from app.config import settings
from app.models.event import Event
from app.models.festival import Festival
from app.models.user import User
from .app_setting_service import AppSettingService
from .calendar_service import CalendarService

MAX_LINE_OCTETS = 75
TRUNCATED_PROPERTY = "X-WR-CLAKETTES-TRUNCATED"


def _fold(line: str) -> list[str]:
    """Split one content line into folded lines of at most 75 octets each.

    Folding counts octets, not characters, and never cuts inside a UTF-8
    multi-byte sequence: a cut that would land on a continuation byte moves back
    to the preceding character boundary. Every continuation carries a single
    leading space, so the leading space is budgeted out of the 75 octets it
    still leaves for content.
    """
    data = line.encode("utf-8")
    if len(data) <= MAX_LINE_OCTETS:
        return [line]
    chunks: list[str] = []
    budget = MAX_LINE_OCTETS
    while data:
        cut = budget
        while 1 < cut < len(data) and (data[cut] & 0xC0) == 0x80:
            cut -= 1
        chunks.append(data[:cut].decode("utf-8"))
        data = data[cut:]
        budget = MAX_LINE_OCTETS - 1
    return chunks


def _calendar_body(lines: list[str]) -> str:
    """Join content lines into an iCalendar stream: folded, CRLF terminated."""
    physical: list[str] = []
    for line in lines:
        chunks = _fold(line)
        physical.append(chunks[0])
        physical.extend(" " + chunk for chunk in chunks[1:])
    return "\r\n".join(physical) + "\r\n"


def _as_utc(stamp: datetime) -> datetime:
    """Read a naive database timestamp as UTC, matching the stored convention."""
    if stamp.tzinfo is None:
        return stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc)


def _event_dtstamp(event: Event) -> str:
    """RFC 5545 3.8.7.2: DTSTAMP is when the instance entered the store.

    Read from the event's own row instead of the clock so an unchanged
    resource serialises to the same bytes as its ETag advertises.
    """
    from .export_service import _utc_format

    stamp = event.updated_at or event.created_at
    if stamp is None:
        stamp = datetime.now(timezone.utc)
    return _utc_format(_as_utc(stamp))


def _event_sequence(event: Event) -> int:
    """RFC 5545 3.8.1.9: revision counter of one VEVENT, never negative.

    Counted in whole seconds from the event's own ``created_at`` to
    ``updated_at`` — the same pair of columns that already produce DTSTAMP,
    LAST-MODIFIED and the resource ETag — so SEQUENCE is a pure, reproducible
    function of the row, cannot move without the event actually changing, and
    is never below zero. A brand new event reads 0; every later write lands on
    the elapsed time since it was created.
    """
    stamp = event.updated_at or event.created_at
    origin = event.created_at
    if stamp is None or origin is None:
        return 0
    return max(0, int((_as_utc(stamp) - _as_utc(origin)).total_seconds()))


def _ics_categories(value) -> str:
    """RFC 5545 3.8.1.2: CATEGORIES carries a comma-delimited list of values.

    Every entry is DQUOTE-delimited, the interoperable form used by Apple
    Calendar, Google and Thunderbird, so a category whose own text contains a
    comma stays a single value instead of splitting the list in two. The
    delimiter and the comma inside the entry are still escaped as TEXT
    requires, because DQUOTE is not a SAFE-CHAR.
    """
    from .export_service import _ics_text

    return '"{}"'.format(_ics_text(value).replace('"', '\\"'))


def _event_url(event: Event) -> str | None:
    """RFC 5545 3.8.4.6: URL takes a URI, and a URI is absolute.

    Returns None when no public base URL is configured: the property is
    optional, so dropping it is correct where emitting ``/events/<id>`` would
    hand the client a relative reference that Apple Calendar and Thunderbird
    discard or rewrite.
    """
    base = (settings.PUBLIC_BASE_URL or "").strip().rstrip("/")
    if not base:
        return None
    return f"{base}/events/{event.id}"


@dataclass(frozen=True)
class DavCalendar:
    """A CalDAV collection exposed to one user."""

    name: str
    display_name: str
    description: str
    festival_id: int | None


class DavService:
    """CalDAV operations for exposing calendar collections and events."""

    def __init__(self, calendar_service: CalendarService | None = None):
        self.calendar_service = calendar_service or CalendarService()
        self.settings_service = AppSettingService()

    def list_calendars(self, db: Session, user: User) -> list[DavCalendar]:
        """List all visible CalDAV collections for the user."""
        if not self.settings_service.is_calendar_enabled(db):
            return []

        calendars: list[DavCalendar] = []

        calendars.append(
            DavCalendar(
                name=constants.AGENDA_COLLECTION,
                display_name="Agenda",
                description="All festivals",
                festival_id=None,
            )
        )

        festivals = (
            db.query(Festival)
            .filter(Festival.is_active.is_(True), Festival.show_in_calendar.is_(True))
            .order_by(Festival.name)
            .all()
        )
        for festival in festivals:
            calendars.append(
                DavCalendar(
                    name=f"{constants.FESTIVAL_PREFIX}{festival.id}",
                    display_name=festival.name,
                    description=festival.description or "",
                    festival_id=festival.id,
                )
            )
        return calendars

    def calendar_by_name(self, db: Session, user: User, name: str) -> DavCalendar | None:
        """Get a calendar by name."""
        for calendar in self.list_calendars(db, user):
            if calendar.name == name:
                return calendar
        return None

    def collection_festival_id(self, name: str) -> int | None:
        """Extract festival id from collection name."""
        if name == constants.AGENDA_COLLECTION:
            return None
        if name.startswith(constants.FESTIVAL_PREFIX):
            try:
                return int(name[len(constants.FESTIVAL_PREFIX) :])
            except ValueError:
                return None
        return None

    def events(
        self, db: Session, user: User, festival_id: int | None = None, limit: int = constants.DAV_MAX_EVENTS
    ) -> list[Event]:
        """Get events for a collection."""
        festival_ids = [festival_id] if festival_id is not None else None
        query = self.calendar_service.visible_events_query(db, user, festival_ids)
        return query.order_by(Event.start_date, Event.sort_order, Event.id).limit(limit).all()

    def event(self, db: Session, user: User, event_id: int, festival_id: int | None = None) -> Event | None:
        """Get a single event if visible."""
        if not self.settings_service.is_calendar_enabled(db):
            return None

        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None
        if not event.is_active:
            return None
        if not event.festival:
            return None
        if not event.festival.is_active:
            return None
        if not event.festival.show_in_calendar:
            return None
        if not event.is_visible_to(user):
            return None
        if festival_id is not None and event.festival_id != festival_id:
            return None
        return event

    def collection_etag(self, db: Session, user: User, festival_id: int | None = None) -> str | None:
        """Strong ETag for a collection."""
        if not self.settings_service.is_calendar_enabled(db):
            return None

        festival_ids = [festival_id] if festival_id is not None else None
        query = self.calendar_service.visible_events_query(db, user, festival_ids)
        result = query.with_entities(
            func.count(Event.id),
            func.sum(Event.id),
            func.max(Event.updated_at),
        ).first()

        count, sum_id, max_updated = result
        if count == 0:
            max_updated_str = ""
        else:
            max_updated_str = max_updated.isoformat() if max_updated else ""

        content = f"{count}:{sum_id}:{max_updated_str}"
        etag_hash = hashlib.sha1(content.encode("utf-8")).hexdigest()[:20]
        return f'"{etag_hash}"'

    def resource_etag(self, event: Event) -> str:
        """Weak ETag for a resource."""
        updated = event.updated_at.isoformat() if event.updated_at else ""
        content = f"{event.id}:{updated}"
        etag_hash = hashlib.sha1(content.encode("utf-8")).hexdigest()[:20]
        return f'W/"{etag_hash}"'

    def sync_token(self, etag: str) -> str:
        """Generate sync token from etag."""
        etag_clean = etag.strip('"')
        return f"{constants.SYNC_TOKEN_PREFIX}{etag_clean}"

    def etag_from_sync_token(self, token: str | None) -> str | None:
        """Extract etag from sync token."""
        if not token:
            return None
        if not token.startswith(constants.SYNC_TOKEN_PREFIX):
            return None
        etag_part = token[len(constants.SYNC_TOKEN_PREFIX) :]
        if not etag_part:
            return None
        return f'"{etag_part}"'

    def _event_vevent_lines(self, event: Event, festival: Festival, calendar: DavCalendar) -> list[str]:
        from .export_service import _ics_text, _utc_format

        lines: list[str] = []
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:event-{event.id}@clakettes")
        lines.append(f"DTSTAMP:{_event_dtstamp(event)}")
        if event.updated_at:
            lines.append(f"LAST-MODIFIED:{_utc_format(event.updated_at)}")
        start = event.start_date
        end = event.end_date or (start + timedelta(hours=1))
        if end <= start:
            end = start + timedelta(hours=1)
        lines.append(f"DTSTART:{_utc_format(start)}")
        lines.append(f"DTEND:{_utc_format(end)}")
        lines.append(f"SUMMARY:{_ics_text(event.title)}")
        location = event.venue or event.location
        if location:
            lines.append(f"LOCATION:{_ics_text(location)}")
        desc = event.short_description or event.description
        if desc:
            lines.append(f"DESCRIPTION:{_ics_text(desc)}")
        if event.event_type:
            lines.append(f"CATEGORIES:{_ics_categories(event.event_type)}")
        if event.venue_latitude is not None and event.venue_longitude is not None:
            lines.append(f"GEO:{event.venue_latitude};{event.venue_longitude}")
        url = _event_url(event)
        if url:
            lines.append(f"URL:{url}")
        lines.append("STATUS:CONFIRMED")
        lines.append("TRANSP:OPAQUE")
        lines.append(f"SEQUENCE:{_event_sequence(event)}")
        lines.append(f"X-APPLE-STRUCTURE-LOCATION:{_ics_text(festival.name)}")
        lines.append("END:VEVENT")
        return lines

    def event_ics(self, event: Event, festival: Festival, calendar: DavCalendar) -> str:
        """Generate ICS for a single event."""
        lines: list[str] = []
        lines.append("BEGIN:VCALENDAR")
        lines.append("VERSION:2.0")
        lines.append(f"PRODID:{constants.PRODID}")
        lines.extend(self._event_vevent_lines(event, festival, calendar))
        lines.append("END:VCALENDAR")
        return _calendar_body(lines)

    def feed_ics(self, events: list[Event], festivals_by_id: dict[int, Festival], calendar: DavCalendar) -> str:
        """Generate ICS feed for a collection."""
        from .export_service import _ics_text

        lines: list[str] = []
        lines.append("BEGIN:VCALENDAR")
        lines.append("VERSION:2.0")
        lines.append(f"PRODID:{constants.PRODID}")
        lines.append("CALSCALE:GREGORIAN")
        lines.append("METHOD:PUBLISH")
        lines.append(f"X-WR-CALNAME:{_ics_text(calendar.display_name)}")
        lines.append("X-WR-TIMEZONE:UTC")
        if len(events) >= constants.DAV_MAX_EVENTS:
            lines.append(f"{TRUNCATED_PROPERTY}:{constants.DAV_MAX_EVENTS}")
        for event in events:
            festival = festivals_by_id.get(event.festival_id)
            if festival:
                lines.extend(self._event_vevent_lines(event, festival, calendar))
        lines.append("END:VCALENDAR")
        return _calendar_body(lines)
