"""Schemas for the shared agenda across festivals and its visibility settings."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgendaEventResponse(BaseModel):
    """A single event on the shared agenda, enriched with its festival.

    ``is_private`` tells the client the event is only visible to a restricted
    audience, so it can be styled differently. Restricted events are only ever
    returned to users that pass the visibility check.
    """

    id: int
    festival_id: int
    festival_name: str
    title: str
    description: str | None = None
    short_description: str | None = None
    event_type: str = "other"
    start_date: datetime
    end_date: datetime | None = None
    location: str | None = None
    venue: str | None = None
    venue_latitude: float | None = None
    venue_longitude: float | None = None
    image_url: str | None = None
    color: str | None = None
    capacity: int | None = None
    is_active: bool = True
    visibility_scope: str = "public"
    is_private: bool = False
    updated_at: datetime | None = None


class AgendaResponse(BaseModel):
    """The agenda payload consumed by the dashboard and the calendar screen."""

    enabled: bool = True
    festivals: list["AgendaFestivalResponse"] = []
    events: list[AgendaEventResponse] = []
    total: int = 0

    model_config = ConfigDict(from_attributes=True)


class AgendaFestivalResponse(BaseModel):
    """A festival that contributes events to the agenda."""

    id: int
    name: str
    logo_url: str | None = None
    location: str | None = None
    event_count: int = 0


AgendaResponse.model_rebuild()


class CalendarFestivalVisibility(BaseModel):
    """Per-festival inclusion flag shown in the admin settings screen."""

    id: int
    name: str
    logo_url: str | None = None
    location: str | None = None
    is_active: bool = True
    show_in_calendar: bool = True
    event_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CalendarSettingsResponse(BaseModel):
    """Full calendar configuration. Admin-only."""

    calendar_enabled: bool = True
    festivals: list[CalendarFestivalVisibility] = []


class CalendarSettingsPublic(BaseModel):
    """Minimal payload for anonymous visitors — only whether to render the agenda."""

    calendar_enabled: bool = True


class CalendarSettingsUpdate(BaseModel):
    """Admin payload to toggle the agenda and per-festival inclusion.

    Omitted fields are left untouched.
    """

    calendar_enabled: bool | None = None
    festival_ids: list[int] | None = Field(
        None,
        description="Festivals to include in the agenda. Defaults to all when omitted.",
    )


class DavCollectionResponse(BaseModel):
    """One CalDAV collection the signed-in user can subscribe to."""

    name: str
    display_name: str
    description: str | None = None


class DavTokenResponse(BaseModel):
    """Issued by token creation. `token` is returned exactly once."""

    token: str
    expires_at: datetime | None = None
    collections: list[DavCollectionResponse] = []


class DavTokenStatusResponse(BaseModel):
    """Never contains the token itself."""

    has_token: bool
    expires_at: datetime | None = None
    collections: list[DavCollectionResponse] = []
