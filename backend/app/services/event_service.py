"""Event service — business logic for events, tickets, seats, and attendee management."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import (
    Event,
    EventTicketType,
    EventSeat,
    EventReservation,
    EventAttendee,
    SeatStatus,
    AttendeeStatus,
)
from app.models.role import Role
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventTicketTypeCreate,
    EventTicketTypeUpdate,
    EventSeatCreate,
    EventSeatBulkCreate,
    EventSeatUpdate,
    EventReservationCreate,
    EventReservationUpdate,
    EventAttendeeCreate,
    EventAttendeeUpdate,
)
from .base_service import BaseService


class EventService(BaseService[Event, EventCreate, EventUpdate]):
    def __init__(self):
        super().__init__(Event)

    def create(self, db: Session, obj_in: EventCreate, **extra_fields) -> Event:
        data = obj_in.model_dump()
        data.pop("visible_role_ids", None)
        screening_ids = data.pop("screening_shortfilm_ids", None) or []
        data.update(extra_fields)
        db_obj = Event(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        if screening_ids:
            self.set_screenings(db, db_obj, screening_ids)
        return db_obj

    def find_conflict(
        self,
        db: Session,
        festival_id: int,
        venue: str | None,
        start: datetime,
        end: datetime | None,
        exclude_event_id: int | None = None,
    ) -> Event | None:
        if not venue or not venue.strip():
            return None
        end_eff = end or start
        q = db.query(Event).filter(
            Event.festival_id == festival_id,
            Event.venue == venue,
            Event.is_active.is_(True),
            Event.start_date <= end_eff,
        )
        if exclude_event_id is not None:
            q = q.filter(Event.id != exclude_event_id)
        for cand in q.all():
            cand_end = cand.end_date or cand.start_date
            if cand.start_date <= end_eff and cand_end >= start:
                return cand
        return None

    def set_screenings(self, db: Session, event: Event, shortfilm_ids: list[int]) -> Event:
        from app.models.event_screening import EventScreening
        from app.models.shortfilm import ShortFilm

        wanted = list(dict.fromkeys(shortfilm_ids))
        if wanted:
            found = {s.id for s in db.query(ShortFilm).filter(ShortFilm.id.in_(wanted)).all()}
            wanted = [i for i in wanted if i in found]
        db.query(EventScreening).filter(EventScreening.event_id == event.id).delete()
        for pos, sid in enumerate(wanted):
            db.add(EventScreening(event_id=event.id, shortfilm_id=sid, sort_order=pos))
        db.commit()
        db.refresh(event)
        return event

    def occupancy(self, db: Session, event: Event) -> dict:
        registered = (
            db.query(EventAttendee)
            .filter(EventAttendee.event_id == event.id, EventAttendee.status != "cancelled")
            .count()
        )
        capacity = event.capacity
        return {
            "attendee_count": registered,
            "capacity": capacity,
            "available_capacity": (capacity - registered) if capacity is not None else None,
            "is_full": capacity is not None and registered >= capacity,
        }

    def update(self, db: Session, id: int, obj_in: EventUpdate) -> Event | None:
        """Partial update.

        ``visible_role_ids`` is a computed property on the model, so it is
        excluded here and applied separately via :meth:`set_visible_roles`.
        """
        data = obj_in.model_dump(exclude_unset=True)
        role_ids = data.pop("visible_role_ids", None)
        screening_ids = data.pop("screening_shortfilm_ids", None)
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        if role_ids is not None:
            db_obj = self.set_visible_roles(db, db_obj, role_ids)
        if screening_ids is not None:
            db_obj = self.set_screenings(db, db_obj, screening_ids)
        return db_obj

    def set_visible_roles(self, db: Session, event: Event, role_ids: list[int] | None) -> Event:
        """Replace the roles allowed to see *event*.

        Ids that do not exist are ignored; an empty list means no role holder can
        see the event, which is the safe reading of ``ROLES`` with no selection.
        """
        if role_ids is None:
            return event
        wanted = set(role_ids)
        if wanted:
            found = db.query(Role).filter(Role.id.in_(wanted), Role.is_active.is_(True)).all()
            event.visibility_roles = found
        else:
            event.visibility_roles = []
        db.commit()
        db.refresh(event)
        return event

    def get_by_festival(
        self,
        db: Session,
        festival_id: int,
        is_active: bool | None = None,
        is_public: bool | None = None,
        event_type: str | None = None,
    ) -> list[Event]:
        query = db.query(Event).filter(Event.festival_id == festival_id)
        if is_active is not None:
            query = query.filter(Event.is_active == is_active)
        if is_public is not None:
            query = query.filter(Event.is_public == is_public)
        if event_type:
            query = query.filter(Event.event_type == event_type)
        return query.order_by(Event.start_date, Event.sort_order).all()

    def get_by_festival_paginated(
        self,
        db: Session,
        festival_id: int,
        page: int,
        size: int,
        is_active: bool | None = None,
        is_public: bool | None = None,
        event_type: str | None = None,
        start_date_from: datetime | None = None,
        start_date_to: datetime | None = None,
        venue: str | None = None,
    ) -> dict:
        query = db.query(Event).filter(Event.festival_id == festival_id)
        if is_active is not None:
            query = query.filter(Event.is_active == is_active)
        if is_public is not None:
            query = query.filter(Event.is_public == is_public)
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if start_date_from is not None:
            query = query.filter(Event.start_date >= start_date_from)
        if start_date_to is not None:
            query = query.filter(Event.start_date <= start_date_to)
        if venue:
            query = query.filter(Event.venue == venue)
        return self.paginate(query.order_by(Event.start_date, Event.sort_order), page, size)

    def get_by_date_range(
        self,
        db: Session,
        festival_id: int,
        start: datetime,
        end: datetime,
    ) -> list[Event]:
        return (
            db.query(Event)
            .filter(
                Event.festival_id == festival_id,
                Event.start_date >= start,
                Event.start_date <= end,
            )
            .order_by(Event.start_date)
            .all()
        )


class EventTicketTypeService(BaseService[EventTicketType, EventTicketTypeCreate, EventTicketTypeUpdate]):
    def __init__(self):
        super().__init__(EventTicketType)

    def create(self, db: Session, obj_in: EventTicketTypeCreate, **extra_fields) -> EventTicketType:
        data = obj_in.model_dump()
        data.update(extra_fields)
        db_obj = EventTicketType(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_event(self, db: Session, event_id: int) -> list[EventTicketType]:
        return (
            db.query(EventTicketType)
            .filter(EventTicketType.event_id == event_id)
            .order_by(EventTicketType.sort_order)
            .all()
        )

    def get_by_event_paginated(self, db: Session, event_id: int, page: int, size: int) -> dict:
        query = db.query(EventTicketType).filter(EventTicketType.event_id == event_id)
        return self.paginate(query.order_by(EventTicketType.sort_order), page, size)


class EventSeatService(BaseService[EventSeat, EventSeatCreate, EventSeatUpdate]):
    def __init__(self):
        super().__init__(EventSeat)

    def get_by_event(self, db: Session, event_id: int, section: str | None = None) -> list[EventSeat]:
        query = db.query(EventSeat).filter(EventSeat.event_id == event_id)
        if section:
            query = query.filter(EventSeat.section == section)
        return query.order_by(EventSeat.section, EventSeat.row_label, EventSeat.number).all()

    def get_by_event_paginated(
        self,
        db: Session,
        event_id: int,
        page: int,
        size: int,
        section: str | None = None,
    ) -> dict:
        query = db.query(EventSeat).filter(EventSeat.event_id == event_id)
        if section:
            query = query.filter(EventSeat.section == section)
        return self.paginate(query.order_by(EventSeat.section, EventSeat.row_label, EventSeat.number), page, size)

    def bulk_create(self, db: Session, event_id: int, bulk: EventSeatBulkCreate) -> list[EventSeat]:
        existing = {
            (row_label, number)
            for row_label, number in db.query(EventSeat.row_label, EventSeat.number)
            .filter(EventSeat.event_id == event_id, EventSeat.section == bulk.section)
            .all()
        }
        spacing_x = 40
        spacing_y = 40
        created = []
        for row_idx, row_label in enumerate(bulk.rows):
            for i in range(bulk.start_number, bulk.start_number + bulk.numbers_per_row):
                number = i
                if (row_label, number) in existing:
                    continue
                label = f"{bulk.prefix or ''}{row_label}{number}" if bulk.prefix else None
                seat = EventSeat(
                    event_id=event_id,
                    section=bulk.section,
                    row_label=row_label,
                    number=number,
                    label=label or f"{row_label}{number}",
                    ticket_type_id=bulk.ticket_type_id,
                    is_accessible=False,
                    x_position=float(i - bulk.start_number) * spacing_x + 20,
                    y_position=float(row_idx) * spacing_y + 20,
                )
                created.append(seat)
        if not created:
            return created
        try:
            db.add_all(created)
            db.commit()
        except Exception:
            db.rollback()
            raise
        for seat in created:
            db.refresh(seat)
        return created

    def get_sections(self, db: Session, event_id: int) -> list[str]:
        results = (
            db.query(EventSeat.section)
            .filter(
                EventSeat.event_id == event_id,
                EventSeat.section.isnot(None),
            )
            .distinct()
            .all()
        )
        return [r[0] for r in results if r[0]]

    def get_seat_counts(self, db: Session, event_id: int) -> dict:
        total = db.query(EventSeat).filter(EventSeat.event_id == event_id).count()
        available = (
            db.query(EventSeat)
            .filter(
                EventSeat.event_id == event_id,
                EventSeat.status == SeatStatus.AVAILABLE.value,
            )
            .count()
        )
        occupied = total - available
        return {"total": total, "available": available, "occupied": occupied}

    def assign_seat(self, db: Session, seat_id: int, attendee_id: int) -> EventSeat | None:
        seat = self.get(db, seat_id)
        if not seat or seat.status != SeatStatus.AVAILABLE.value:
            return None
        seat.status = SeatStatus.ASSIGNED.value
        db.commit()
        db.refresh(seat)
        return seat

    def release_seat(self, db: Session, seat_id: int) -> EventSeat | None:
        seat = self.get(db, seat_id)
        if not seat:
            return None
        seat.status = SeatStatus.AVAILABLE.value
        seat.attendee = None
        db.commit()
        db.refresh(seat)
        return seat


class EventReservationService(BaseService[EventReservation, EventReservationCreate, EventReservationUpdate]):
    def __init__(self):
        super().__init__(EventReservation)

    def get_by_event(
        self,
        db: Session,
        event_id: int,
        status: str | None = None,
    ) -> list[EventReservation]:
        query = db.query(EventReservation).filter(EventReservation.event_id == event_id)
        if status:
            query = query.filter(EventReservation.status == status)
        return query.order_by(EventReservation.created_at.desc()).all()

    def get_by_event_paginated(
        self,
        db: Session,
        event_id: int,
        page: int,
        size: int,
        status: str | None = None,
    ) -> dict:
        query = db.query(EventReservation).filter(EventReservation.event_id == event_id)
        if status:
            query = query.filter(EventReservation.status == status)
        return self.paginate(query.order_by(EventReservation.created_at.desc()), page, size)

    def get_by_user_and_event(self, db: Session, user_id: int, event_id: int) -> EventReservation | None:
        return (
            db.query(EventReservation)
            .filter(
                EventReservation.event_id == event_id,
                EventReservation.user_id == user_id,
            )
            .first()
        )

    def create_with_attendees(
        self,
        db: Session,
        user_id: int,
        obj_in: EventReservationCreate,
    ) -> EventReservation | None:
        event = db.query(Event).filter(Event.id == obj_in.event_id, Event.is_active).first()
        if not event:
            return None

        reservation = EventReservation(
            event_id=obj_in.event_id,
            user_id=user_id,
            created_by=user_id,
            total_quantity=len(obj_in.attendees) or 1,
            notes=obj_in.notes,
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        for att_data in obj_in.attendees:
            attendee = EventAttendee(
                event_id=obj_in.event_id,
                reservation_id=reservation.id,
                user_id=att_data.user_id,
                seat_id=att_data.seat_id,
                ticket_type_id=att_data.ticket_type_id,
                is_guest=att_data.is_guest,
                guest_name=att_data.guest_name,
                guest_email=att_data.guest_email,
                guest_phone=att_data.guest_phone,
                is_hidden=att_data.is_hidden,
                notes=att_data.notes,
            )
            db.add(attendee)

            # Mark seat as assigned if provided
            if att_data.seat_id:
                seat = db.query(EventSeat).filter(EventSeat.id == att_data.seat_id).first()
                if seat and seat.status == SeatStatus.AVAILABLE.value:
                    seat.status = SeatStatus.ASSIGNED.value

        db.commit()
        db.refresh(reservation)
        return reservation

    def confirm(self, db: Session, reservation_id: int) -> EventReservation | None:
        res = self.get(db, reservation_id)
        if not res or res.status != "pending":
            return None
        res.status = "confirmed"
        res.confirmed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(res)
        return res

    def cancel(self, db: Session, reservation_id: int) -> EventReservation | None:
        res = self.get(db, reservation_id)
        if not res or res.status == "cancelled":
            return None
        res.status = "cancelled"
        res.cancelled_at = datetime.now(timezone.utc)
        # Release seats
        for att in res.attendees:
            if att.seat_id:
                seat = db.query(EventSeat).filter(EventSeat.id == att.seat_id).first()
                if seat:
                    seat.status = SeatStatus.AVAILABLE.value
        db.commit()
        db.refresh(res)
        return res


class EventAttendeeService(BaseService[EventAttendee, EventAttendeeCreate, EventAttendeeUpdate]):
    def __init__(self):
        super().__init__(EventAttendee)

    def get_by_event(
        self,
        db: Session,
        event_id: int,
        status: str | None = None,
        include_hidden: bool = False,
    ) -> list[EventAttendee]:
        query = db.query(EventAttendee).filter(EventAttendee.event_id == event_id)
        if status:
            query = query.filter(EventAttendee.status == status)
        if not include_hidden:
            query = query.filter(~EventAttendee.is_hidden)
        return query.order_by(EventAttendee.created_at).all()

    def get_by_event_paginated(
        self,
        db: Session,
        event_id: int,
        page: int,
        size: int,
        status: str | None = None,
        include_hidden: bool = False,
    ) -> dict:
        query = db.query(EventAttendee).filter(EventAttendee.event_id == event_id)
        if status:
            query = query.filter(EventAttendee.status == status)
        if not include_hidden:
            query = query.filter(~EventAttendee.is_hidden)
        return self.paginate(query.order_by(EventAttendee.created_at), page, size)

    def get_events_for_user(self, db: Session, user_id: int) -> list[Event]:
        attendee_ids = select(EventAttendee.event_id).where(EventAttendee.user_id == user_id)
        return db.query(Event).filter(Event.id.in_(attendee_ids)).all()

    def create_with_seat(
        self,
        db: Session,
        obj_in: EventAttendeeCreate,
        event_id: int,
        invited_by: int,
    ) -> EventAttendee:
        data = obj_in.model_dump()
        data["event_id"] = event_id
        data["invited_by"] = invited_by
        db_obj = EventAttendee(**data)
        db.add(db_obj)
        if obj_in.seat_id:
            seat = db.query(EventSeat).filter(EventSeat.id == obj_in.seat_id).first()
            if seat:
                seat.status = SeatStatus.ASSIGNED.value
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_with_seat_release(self, db: Session, attendee_id: int) -> bool:
        db_obj = self.get(db, attendee_id)
        if not db_obj:
            return False
        if db_obj.seat_id:
            seat = db.query(EventSeat).filter(EventSeat.id == db_obj.seat_id).first()
            if seat:
                seat.status = SeatStatus.AVAILABLE.value
        db.delete(db_obj)
        db.commit()
        return True

    def assign_vip(
        self,
        db: Session,
        event_id: int,
        user_id: int,
        invited_by: int,
        seat_id: int | None = None,
        ticket_type_id: int | None = None,
        is_hidden: bool = False,
    ) -> EventAttendee:
        """Assign a VIP/guest/organizer seat to a user."""
        attendee = EventAttendee(
            event_id=event_id,
            user_id=user_id,
            seat_id=seat_id,
            ticket_type_id=ticket_type_id,
            invited_by=invited_by,
            is_hidden=is_hidden,
            status=AttendeeStatus.REGISTERED.value,
        )
        db.add(attendee)
        if seat_id:
            seat = db.query(EventSeat).filter(EventSeat.id == seat_id).first()
            if seat and seat.status == SeatStatus.AVAILABLE.value:
                seat.status = SeatStatus.ASSIGNED.value
        db.commit()
        db.refresh(attendee)
        return attendee

    def check_in(self, db: Session, attendee_id: int) -> EventAttendee | None:
        att = self.get(db, attendee_id)
        if not att:
            return None
        att.status = AttendeeStatus.ATTENDED.value
        att.checked_in_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(att)
        return att

    def get_attendee_counts(self, db: Session, event_id: int) -> dict:
        total = db.query(EventAttendee).filter(EventAttendee.event_id == event_id).count()
        attended = (
            db.query(EventAttendee)
            .filter(
                EventAttendee.event_id == event_id,
                EventAttendee.status == AttendeeStatus.ATTENDED.value,
            )
            .count()
        )
        no_show = (
            db.query(EventAttendee)
            .filter(
                EventAttendee.event_id == event_id,
                EventAttendee.status == AttendeeStatus.NO_SHOW.value,
            )
            .count()
        )
        registered = (
            db.query(EventAttendee)
            .filter(
                EventAttendee.event_id == event_id,
                EventAttendee.status == AttendeeStatus.REGISTERED.value,
            )
            .count()
        )
        return {
            "total": total,
            "attended": attended,
            "no_show": no_show,
            "registered": registered,
        }
