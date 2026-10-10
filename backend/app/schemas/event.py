from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PageBase


class EventBase(BaseModel):
    festival_id: int
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
    has_external_page: bool = False
    external_url: str | None = None
    internal_page_enabled: bool = True
    capacity: int | None = None
    show_seat_map: bool = False
    is_public: bool = True
    is_active: bool = True
    visibility_scope: str = "public"
    image_url: str | None = None
    color: str | None = None
    sort_order: int = 0


class EventCreate(EventBase):
    visible_role_ids: list[int] = []
    screening_shortfilm_ids: list[int] = []


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    short_description: str | None = None
    event_type: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    location: str | None = None
    venue: str | None = None
    venue_latitude: float | None = None
    venue_longitude: float | None = None
    has_external_page: bool | None = None
    external_url: str | None = None
    internal_page_enabled: bool | None = None
    capacity: int | None = None
    show_seat_map: bool | None = None
    is_public: bool | None = None
    is_active: bool | None = None
    visibility_scope: str | None = None
    image_url: str | None = None
    color: str | None = None
    sort_order: int | None = None
    visible_role_ids: list[int] | None = None
    screening_shortfilm_ids: list[int] | None = None


class EventResponse(EventBase):
    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime
    visible_role_ids: list[int] = []
    screening_shortfilm_ids: list[int] = []
    ticket_types: list["EventTicketTypeResponse"] = []
    seat_count: int = 0
    attendee_count: int = 0
    available_capacity: int | None = None

    model_config = ConfigDict(from_attributes=True)


class EventTicketTypeBase(BaseModel):
    event_id: int
    name: str
    description: str | None = None
    price: float = 0.0
    currency: str = "EUR"
    capacity: int | None = None
    is_active: bool = True
    is_hidden: bool = False
    sort_order: int = 0
    color: str | None = None


class EventTicketTypeCreate(EventTicketTypeBase):
    pass


class EventTicketTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    capacity: int | None = None
    is_active: bool | None = None
    is_hidden: bool | None = None
    sort_order: int | None = None
    color: str | None = None


class EventTicketTypeResponse(EventTicketTypeBase):
    id: int
    sold_count: int
    reserved_count: int
    assigned_count: int
    available_count: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventSeatBase(BaseModel):
    event_id: int
    ticket_type_id: int | None = None
    section: str | None = None
    row_label: str
    number: int
    label: str | None = None
    status: str = "available"
    x_position: float | None = None
    y_position: float | None = None
    is_accessible: bool = False
    notes: str | None = None


class EventSeatCreate(BaseModel):
    section: str | None = None
    row_label: str
    number: int
    label: str | None = None
    ticket_type_id: int | None = None
    is_accessible: bool = False
    x_position: float | None = None
    y_position: float | None = None


class EventSeatBulkCreate(BaseModel):
    section: str | None = None
    rows: list[str] = []
    numbers_per_row: int = 10
    start_number: int = 1
    ticket_type_id: int | None = None
    prefix: str | None = None


class EventSeatUpdate(BaseModel):
    ticket_type_id: int | None = None
    section: str | None = None
    row_label: str | None = None
    number: int | None = None
    label: str | None = None
    status: str | None = None
    x_position: float | None = None
    y_position: float | None = None
    is_accessible: bool | None = None
    notes: str | None = None


class EventSeatResponse(EventSeatBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventAttendeeBase(BaseModel):
    event_id: int
    reservation_id: int | None = None
    user_id: int | None = None
    seat_id: int | None = None
    ticket_type_id: int | None = None
    status: str = "registered"
    invited_by: int | None = None
    is_guest: bool = False
    is_hidden: bool = False
    guest_name: str | None = None
    guest_email: str | None = None
    guest_phone: str | None = None
    notes: str | None = None


class EventAttendeeCreate(BaseModel):
    user_id: int | None = None
    seat_id: int | None = None
    ticket_type_id: int | None = None
    is_guest: bool = False
    guest_name: str | None = None
    guest_email: str | None = None
    guest_phone: str | None = None
    is_hidden: bool = False
    notes: str | None = None


class EventAttendeeUpdate(BaseModel):
    status: str | None = None
    seat_id: int | None = None
    ticket_type_id: int | None = None
    is_hidden: bool | None = None
    guest_name: str | None = None
    guest_email: str | None = None
    guest_phone: str | None = None
    notes: str | None = None


class EventAttendeeResponse(EventAttendeeBase):
    id: int
    checked_in_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    user: Optional["UserResponse"] = None
    seat: EventSeatResponse | None = None
    ticket_type: EventTicketTypeResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class EventReservationBase(BaseModel):
    event_id: int
    user_id: int | None = None
    status: str = "pending"
    total_quantity: int = 1
    notes: str | None = None
    is_hidden: bool = False


class EventReservationCreate(BaseModel):
    event_id: int
    notes: str | None = None
    attendees: list[EventAttendeeCreate] = []


class EventReservationUpdate(BaseModel):
    status: str | None = None
    total_quantity: int | None = None
    notes: str | None = None
    is_hidden: bool | None = None


class EventReservationResponse(EventReservationBase):
    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: datetime | None = None
    cancelled_at: datetime | None = None
    attendees: list[EventAttendeeResponse] = []

    model_config = ConfigDict(from_attributes=True)


class EventPage(PageBase):
    items: list[EventResponse]


class EventTicketTypePage(PageBase):
    items: list[EventTicketTypeResponse]


class EventSeatPage(PageBase):
    items: list[EventSeatResponse]


class EventReservationPage(PageBase):
    items: list[EventReservationResponse]


class EventAttendeePage(PageBase):
    items: list[EventAttendeeResponse]


# Forward references
from .user import UserResponse  # noqa: E402

EventResponse.model_rebuild()
EventReservationResponse.model_rebuild()
EventAttendeeResponse.model_rebuild()
