"""Event/Gala model — festivals can organize events with ticketing, seating, and guest management."""

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
from app.enums import EventType, SeatStatus, AttendeeStatus, EventVisibilityScope

event_visibility_roles = Table(
    "event_visibility_roles",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Event(BaseModel):
    """An event or gala organized within a festival.

    Supports capacity control, seat maps, ticket types, and guest/VIP management.
    Ticket sales use external tools; management is internal.

    ``visibility_scope`` controls who sees the event on the shared agenda.
    When it is ``EventVisibilityScope.ROLES``, the allowed roles are listed in
    the ``event_visibility_roles`` table (see ``visibility_roles``).
    """

    __tablename__ = "events"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    event_type = Column(String(50), nullable=False, default=EventType.OTHER.value)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    location = Column(String(300), nullable=True)
    venue = Column(String(300), nullable=True)
    venue_latitude = Column(Float, nullable=True)
    venue_longitude = Column(Float, nullable=True)

    has_external_page = Column(Boolean, default=False)
    external_url = Column(String(500), nullable=True)
    internal_page_enabled = Column(Boolean, default=True)

    capacity = Column(Integer, nullable=True)
    show_seat_map = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    visibility_scope = Column(String(30), nullable=False, default=EventVisibilityScope.PUBLIC.value, index=True)
    image_url = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color for calendar/gantt

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    sort_order = Column(Integer, default=0)

    festival = relationship("Festival", back_populates="events")
    ticket_types = relationship("EventTicketType", back_populates="event", cascade="all, delete-orphan")
    seats = relationship("EventSeat", back_populates="event", cascade="all, delete-orphan")
    reservations = relationship("EventReservation", back_populates="event", cascade="all, delete-orphan")
    attendees = relationship("EventAttendee", back_populates="event", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    awards = relationship("Award", back_populates="event")
    rulebooks = relationship("FestivalRulebook", back_populates="event")
    screenings = relationship(
        "EventScreening", back_populates="event", cascade="all, delete-orphan", order_by="EventScreening.sort_order"
    )
    visibility_roles = relationship("Role", secondary=event_visibility_roles, lazy="selectin")

    @property
    def screening_shortfilm_ids(self) -> list[int]:
        items = sorted(self.screenings or [], key=lambda s: s.sort_order or 0)
        return [s.shortfilm_id for s in items]

    @property
    def visible_role_ids(self) -> list[int]:
        """Ids of the roles allowed to see this event (empty unless scope is ROLES)."""
        return [role.id for role in self.visibility_roles]

    def is_visible_to(self, user) -> bool:
        """Return True when *user* (may be None) may see this event.

        Mirrors the SQL used by ``CalendarService`` so both paths agree.
        """
        scope = self.visibility_scope or EventVisibilityScope.PUBLIC.value
        if scope == EventVisibilityScope.PUBLIC.value:
            return True
        if user is None:
            return False
        if scope == EventVisibilityScope.ATTENDEES_ONLY.value:
            return any(a.user_id == user.id and not a.is_hidden for a in self.attendees)
        if scope == EventVisibilityScope.FESTIVAL_MEMBERS.value:
            return any(f.id == self.festival_id for f in user.festivals)
        role_ids = {r.id for r in self.visibility_roles}
        if not role_ids:
            return False
        return any(
            ur.role_id in role_ids and (ur.festival_id == self.festival_id or ur.festival_id is None)
            for ur in user.user_roles
        )

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', type='{self.event_type}')>"


class EventTicketType(BaseModel):
    """Ticket type for an event — defines price, capacity, and availability."""

    __tablename__ = "event_ticket_types"

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, default=0.0)
    currency = Column(String(3), default="EUR")
    capacity = Column(Integer, nullable=True)
    sold_count = Column(Integer, default=0)
    reserved_count = Column(Integer, default=0)
    assigned_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    color = Column(String(7), nullable=True)  # Color for seat map

    event = relationship("Event", back_populates="ticket_types")
    attendees = relationship("EventAttendee", back_populates="ticket_type")
    seats = relationship("EventSeat", back_populates="ticket_type")

    @property
    def available_count(self) -> int:
        if self.capacity is None:
            return None
        return self.capacity - self.sold_count - self.reserved_count - self.assigned_count

    def __repr__(self):
        return f"<EventTicketType(name='{self.name}', price={self.price})>"


class EventSeat(BaseModel):
    """Individual seat within an event venue (for seat selection/assignment)."""

    __tablename__ = "event_seats"

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    ticket_type_id = Column(Integer, ForeignKey("event_ticket_types.id"), nullable=True)
    section = Column(String(100), nullable=True)  # e.g., "Patio", "Balcony", "VIP"
    row_label = Column(String(10), nullable=False)
    number = Column(Integer, nullable=False)
    label = Column(String(20), nullable=True)  # Custom label
    status = Column(String(20), nullable=False, default=SeatStatus.AVAILABLE.value)
    x_position = Column(Float, nullable=True)  # For visual seat map
    y_position = Column(Float, nullable=True)  # For visual seat map
    is_accessible = Column(Boolean, default=False)  # Wheelchair accessible
    notes = Column(Text, nullable=True)

    event = relationship("Event", back_populates="seats")
    ticket_type = relationship("EventTicketType", back_populates="seats")
    attendee = relationship("EventAttendee", back_populates="seat", uselist=False)

    def __repr__(self):
        return f"<EventSeat(event_id={self.event_id}, {self.row_label}{self.number})>"

    class Meta:
        unique_together = ("event_id", "section", "row_label", "number")


class EventReservation(BaseModel):
    """A reservation for an event — groups one or more attendees under a booking."""

    __tablename__ = "event_reservations"

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who made the reservation
    status = Column(String(20), nullable=False, default="pending")
    total_quantity = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_hidden = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="reservations")
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    attendees = relationship("EventAttendee", back_populates="reservation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EventReservation(id={self.id}, status='{self.status}')>"


class EventAttendee(BaseModel):
    """Individual attendee of an event — may have a reserved/assigned seat."""

    __tablename__ = "event_attendees"

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    reservation_id = Column(Integer, ForeignKey("event_reservations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Platform user (nullable for guests)
    seat_id = Column(Integer, ForeignKey("event_seats.id"), nullable=True)
    ticket_type_id = Column(Integer, ForeignKey("event_ticket_types.id"), nullable=True)

    status = Column(String(20), nullable=False, default=AttendeeStatus.REGISTERED.value)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who assigned/invited
    is_guest = Column(Boolean, default=False)  # Non-platform user
    is_hidden = Column(Boolean, default=False)  # Hidden from public view
    guest_name = Column(String(200), nullable=True)
    guest_email = Column(String(200), nullable=True)
    guest_phone = Column(String(50), nullable=True)
    checked_in_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    event = relationship("Event", back_populates="attendees")
    reservation = relationship("EventReservation", back_populates="attendees")
    user = relationship("User", foreign_keys=[user_id])
    seat = relationship("EventSeat", back_populates="attendee")
    ticket_type = relationship("EventTicketType", back_populates="attendees")
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self):
        name = self.guest_name or f"user={self.user_id}"
        return f"<EventAttendee(event_id={self.event_id}, {name})>"
