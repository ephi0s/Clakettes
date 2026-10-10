from datetime import datetime

from app.models.event import (
    EventSeat,
    EventReservation,
    EventAttendee,
    SeatStatus,
    AttendeeStatus,
)
from app.schemas.event import (
    EventCreate,
    EventTicketTypeCreate,
    EventSeatBulkCreate,
    EventReservationCreate,
    EventAttendeeCreate,
)
from app.services.event_service import (
    EventService,
    EventTicketTypeService,
    EventSeatService,
    EventReservationService,
    EventAttendeeService,
)


class TestEventService:
    def test_create_with_extra_fields(self, db_session, create_festival):
        svc = EventService()
        festival = create_festival()
        obj_in = EventCreate(
            festival_id=festival.id,
            title="Test Event",
            event_type="screening",
            start_date=datetime(2026, 7, 1),
        )
        event = svc.create(db_session, obj_in, created_by=42)
        assert event.id is not None
        assert event.title == "Test Event"
        assert event.created_by == 42

    def test_get_by_festival(self, db_session, create_festival, create_event):
        svc = EventService()
        festival = create_festival()
        create_event(festival_id=festival.id)
        create_event(festival_id=festival.id)
        events = svc.get_by_festival(db_session, festival.id)
        assert len(events) == 2

    def test_get_by_festival_with_is_active(self, db_session, create_festival, create_event):
        svc = EventService()
        festival = create_festival()
        e1 = create_event(festival_id=festival.id, is_active=True)
        create_event(festival_id=festival.id, is_active=False)
        events = svc.get_by_festival(db_session, festival.id, is_active=True)
        assert len(events) == 1
        assert events[0].id == e1.id

    def test_get_by_festival_with_is_public(self, db_session, create_festival):
        svc = EventService()
        festival = create_festival()
        e1 = svc.create(
            db_session,
            EventCreate(
                festival_id=festival.id,
                title="Public",
                event_type="screening",
                start_date=datetime(2026, 7, 1),
                is_public=True,
            ),
        )
        svc.create(
            db_session,
            EventCreate(
                festival_id=festival.id,
                title="Private",
                event_type="screening",
                start_date=datetime(2026, 7, 1),
                is_public=False,
            ),
        )
        events = svc.get_by_festival(db_session, festival.id, is_public=True)
        assert len(events) == 1
        assert events[0].id == e1.id

    def test_get_by_festival_with_event_type(self, db_session, create_festival, create_event):
        svc = EventService()
        festival = create_festival()
        create_event(festival_id=festival.id, event_type="screening")
        e2 = create_event(festival_id=festival.id, event_type="workshop")
        events = svc.get_by_festival(db_session, festival.id, event_type="workshop")
        assert len(events) == 1
        assert events[0].id == e2.id

    def test_get_by_date_range(self, db_session, create_festival, create_event):
        svc = EventService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        start = datetime(2026, 6, 1)
        end = datetime(2026, 8, 1)
        events = svc.get_by_date_range(db_session, festival.id, start, end)
        assert len(events) == 1
        assert events[0].id == event.id

    def test_get_by_date_range_no_match(self, db_session, create_festival, create_event):
        svc = EventService()
        festival = create_festival()
        create_event(festival_id=festival.id)
        start = datetime(2026, 8, 1)
        end = datetime(2026, 9, 1)
        events = svc.get_by_date_range(db_session, festival.id, start, end)
        assert len(events) == 0

    def test_get_non_existent(self, db_session):
        svc = EventService()
        event = svc.get(db_session, 999)
        assert event is None


class TestEventTicketTypeService:
    def test_create(self, db_session, create_festival, create_event):
        svc = EventTicketTypeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        obj_in = EventTicketTypeCreate(event_id=event.id, name="Standard", price=10.0)
        tt = svc.create(db_session, obj_in)
        assert tt.id is not None
        assert tt.name == "Standard"
        assert tt.price == 10.0

    def test_create_with_extra_fields(self, db_session, create_festival, create_event):
        svc = EventTicketTypeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        obj_in = EventTicketTypeCreate(event_id=event.id, name="VIP", price=50.0)
        tt = svc.create(db_session, obj_in, color="#FF0000")
        assert tt.color == "#FF0000"

    def test_get_by_event(self, db_session, create_festival, create_event):
        svc = EventTicketTypeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        svc.create(db_session, EventTicketTypeCreate(event_id=event.id, name="Standard", price=10.0))
        svc.create(db_session, EventTicketTypeCreate(event_id=event.id, name="VIP", price=50.0))
        types = svc.get_by_event(db_session, event.id)
        assert len(types) == 2

    def test_get_by_event_empty(self, db_session, create_festival, create_event):
        svc = EventTicketTypeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        types = svc.get_by_event(db_session, event.id)
        assert types == []


class TestEventSeatService:
    def test_get_by_event(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        seats = [
            EventSeat(event_id=event.id, row_label="A", number=1, section="main"),
            EventSeat(event_id=event.id, row_label="A", number=2, section="main"),
            EventSeat(event_id=event.id, row_label="B", number=1, section="balcony"),
        ]
        for s in seats:
            db_session.add(s)
        db_session.commit()
        result = svc.get_by_event(db_session, event.id)
        assert len(result) == 3

    def test_get_by_event_with_section(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        seats = [
            EventSeat(event_id=event.id, row_label="A", number=1, section="main"),
            EventSeat(event_id=event.id, row_label="A", number=2, section="main"),
            EventSeat(event_id=event.id, row_label="B", number=1, section="balcony"),
        ]
        for s in seats:
            db_session.add(s)
        db_session.commit()
        result = svc.get_by_event(db_session, event.id, section="main")
        assert len(result) == 2
        result = svc.get_by_event(db_session, event.id, section="balcony")
        assert len(result) == 1

    def test_bulk_create(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        bulk = EventSeatBulkCreate(section="orchestra", rows=["A", "B"], numbers_per_row=3, start_number=1)
        seats = svc.bulk_create(db_session, event.id, bulk)
        assert len(seats) == 6
        assert seats[0].section == "orchestra"
        assert seats[0].row_label == "A"
        assert seats[0].number == 1
        assert seats[0].label == "A1"

    def test_bulk_create_with_prefix(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        bulk = EventSeatBulkCreate(section="vip", rows=["A"], numbers_per_row=2, start_number=1, prefix="VIP-")
        seats = svc.bulk_create(db_session, event.id, bulk)
        assert len(seats) == 2
        assert seats[0].label == "VIP-A1"
        assert seats[1].label == "VIP-A2"

    def test_bulk_create_skips_existing(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        bulk = EventSeatBulkCreate(section="main", rows=["A"], numbers_per_row=2, start_number=1)
        assert len(svc.bulk_create(db_session, event.id, bulk)) == 2
        assert len(svc.bulk_create(db_session, event.id, bulk)) == 0

    def test_get_sections(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        seats = [
            EventSeat(event_id=event.id, row_label="A", number=1, section="main"),
            EventSeat(event_id=event.id, row_label="A", number=2, section="main"),
            EventSeat(event_id=event.id, row_label="B", number=1, section="balcony"),
            EventSeat(event_id=event.id, row_label="C", number=1, section="balcony"),
        ]
        for s in seats:
            db_session.add(s)
        db_session.commit()
        sections = svc.get_sections(db_session, event.id)
        assert sorted(sections) == ["balcony", "main"]

    def test_get_seat_counts(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        seats = [
            EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.AVAILABLE.value),
            EventSeat(event_id=event.id, row_label="A", number=2, status=SeatStatus.AVAILABLE.value),
            EventSeat(event_id=event.id, row_label="B", number=1, status=SeatStatus.ASSIGNED.value),
        ]
        for s in seats:
            db_session.add(s)
        db_session.commit()
        counts = svc.get_seat_counts(db_session, event.id)
        assert counts["total"] == 3
        assert counts["available"] == 2
        assert counts["occupied"] == 1

    def test_get_seat_counts_none(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        counts = svc.get_seat_counts(db_session, event.id)
        assert counts["total"] == 0
        assert counts["available"] == 0
        assert counts["occupied"] == 0

    def test_assign_seat_success(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        seat = EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.AVAILABLE.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        result = svc.assign_seat(db_session, seat.id, attendee_id=1)
        assert result is not None
        assert result.status == SeatStatus.ASSIGNED.value

    def test_assign_seat_already_assigned(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        seat = EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.ASSIGNED.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        result = svc.assign_seat(db_session, seat.id, attendee_id=1)
        assert result is None

    def test_assign_seat_not_found(self, db_session):
        svc = EventSeatService()
        result = svc.assign_seat(db_session, 999, attendee_id=1)
        assert result is None

    def test_release_seat(self, db_session, create_festival, create_event):
        svc = EventSeatService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        seat = EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.ASSIGNED.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        result = svc.release_seat(db_session, seat.id)
        assert result is not None
        assert result.status == SeatStatus.AVAILABLE.value

    def test_release_seat_not_found(self, db_session):
        svc = EventSeatService()
        result = svc.release_seat(db_session, 999)
        assert result is None


class TestEventReservationService:
    def test_get_by_event(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        r1 = EventReservation(event_id=event.id, user_id=user.id, status="pending")
        r2 = EventReservation(event_id=event.id, user_id=user.id, status="confirmed")
        db_session.add_all([r1, r2])
        db_session.commit()
        result = svc.get_by_event(db_session, event.id)
        assert len(result) == 2

    def test_get_by_event_with_status(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        r1 = EventReservation(event_id=event.id, user_id=user.id, status="pending")
        r2 = EventReservation(event_id=event.id, user_id=user.id, status="confirmed")
        db_session.add_all([r1, r2])
        db_session.commit()
        result = svc.get_by_event(db_session, event.id, status="confirmed")
        assert len(result) == 1
        assert result[0].id == r2.id

    def test_get_by_user_and_event(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        res = EventReservation(event_id=event.id, user_id=user.id, status="pending")
        db_session.add(res)
        db_session.commit()
        result = svc.get_by_user_and_event(db_session, user.id, event.id)
        assert result is not None
        assert result.id == res.id

    def test_get_by_user_and_event_not_found(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        result = svc.get_by_user_and_event(db_session, user.id, event.id)
        assert result is None

    def test_create_with_attendees_success(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id, is_active=True)
        user = create_user()
        seat = EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.AVAILABLE.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        create_data = EventReservationCreate(
            event_id=event.id,
            notes="Test reservation",
            attendees=[EventAttendeeCreate(user_id=user.id, seat_id=seat.id)],
        )
        res = svc.create_with_attendees(db_session, user.id, create_data)
        assert res is not None
        assert res.event_id == event.id
        assert res.user_id == user.id
        assert res.total_quantity == 1
        assert res.notes == "Test reservation"
        assert len(res.attendees) == 1
        assert res.attendees[0].user_id == user.id
        assert res.attendees[0].seat_id == seat.id
        db_session.refresh(seat)
        assert seat.status == SeatStatus.ASSIGNED.value

    def test_create_with_attendees_no_attendees(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id, is_active=True)
        user = create_user()
        create_data = EventReservationCreate(event_id=event.id)
        res = svc.create_with_attendees(db_session, user.id, create_data)
        assert res is not None
        assert res.total_quantity == 1
        assert res.attendees == []

    def test_create_with_attendees_event_inactive(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id, is_active=False)
        user = create_user()
        create_data = EventReservationCreate(event_id=event.id)
        res = svc.create_with_attendees(db_session, user.id, create_data)
        assert res is None

    def test_confirm(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        res = EventReservation(event_id=event.id, user_id=user.id, status="pending")
        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        result = svc.confirm(db_session, res.id)
        assert result is not None
        assert result.status == "confirmed"
        assert result.confirmed_at is not None

    def test_confirm_already_confirmed(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        res = EventReservation(event_id=event.id, user_id=user.id, status="confirmed")
        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        result = svc.confirm(db_session, res.id)
        assert result is None

    def test_confirm_not_found(self, db_session):
        svc = EventReservationService()
        result = svc.confirm(db_session, 999)
        assert result is None

    def test_cancel(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        res = EventReservation(event_id=event.id, user_id=user.id, status="pending")
        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        result = svc.cancel(db_session, res.id)
        assert result is not None
        assert result.status == "cancelled"
        assert result.cancelled_at is not None

    def test_cancel_already_cancelled(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        res = EventReservation(event_id=event.id, user_id=user.id, status="cancelled")
        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        result = svc.cancel(db_session, res.id)
        assert result is None

    def test_cancel_not_found(self, db_session):
        svc = EventReservationService()
        result = svc.cancel(db_session, 999)
        assert result is None

    def test_cancel_releases_seats(self, db_session, create_festival, create_event, create_user):
        svc = EventReservationService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        seat = EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.ASSIGNED.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        res = EventReservation(event_id=event.id, user_id=user.id, status="pending")
        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        att = EventAttendee(event_id=event.id, reservation_id=res.id, seat_id=seat.id, user_id=user.id)
        db_session.add(att)
        db_session.commit()
        result = svc.cancel(db_session, res.id)
        assert result.status == "cancelled"
        db_session.refresh(seat)
        assert seat.status == SeatStatus.AVAILABLE.value


class TestEventAttendeeService:
    def test_get_by_event(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        a1 = EventAttendee(event_id=event.id, user_id=user.id)
        a2 = EventAttendee(event_id=event.id, user_id=user.id)
        db_session.add_all([a1, a2])
        db_session.commit()
        result = svc.get_by_event(db_session, event.id)
        assert len(result) == 2

    def test_get_by_event_with_status(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        a1 = EventAttendee(event_id=event.id, user_id=user.id, status=AttendeeStatus.REGISTERED.value)
        a2 = EventAttendee(event_id=event.id, user_id=user.id, status=AttendeeStatus.ATTENDED.value)
        db_session.add_all([a1, a2])
        db_session.commit()
        result = svc.get_by_event(db_session, event.id, status=AttendeeStatus.ATTENDED.value)
        assert len(result) == 1
        assert result[0].id == a2.id

    def test_get_by_event_include_hidden(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        a1 = EventAttendee(event_id=event.id, user_id=user.id, is_hidden=True)
        a2 = EventAttendee(event_id=event.id, user_id=user.id, is_hidden=False)
        db_session.add_all([a1, a2])
        db_session.commit()
        result = svc.get_by_event(db_session, event.id)
        assert len(result) == 1
        assert result[0].id == a2.id
        result = svc.get_by_event(db_session, event.id, include_hidden=True)
        assert len(result) == 2

    def test_get_events_for_user(self, db_session, create_festival, create_event, create_user):
        att_svc = EventAttendeeService()
        festival = create_festival()
        event1 = create_event(festival_id=festival.id)
        event2 = create_event(festival_id=festival.id)
        user = create_user()
        for evt in [event1, event2]:
            db_session.add(EventAttendee(event_id=evt.id, user_id=user.id))
        db_session.commit()
        events = att_svc.get_events_for_user(db_session, user.id)
        assert len(events) == 2
        assert set(e.id for e in events) == {event1.id, event2.id}

    def test_get_events_for_user_none(self, db_session, create_user):
        att_svc = EventAttendeeService()
        user = create_user()
        events = att_svc.get_events_for_user(db_session, user.id)
        assert events == []

    def test_create_with_seat(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        seat = EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.AVAILABLE.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        obj_in = EventAttendeeCreate(user_id=user.id, seat_id=seat.id)
        attendee = svc.create_with_seat(db_session, obj_in, event_id=event.id, invited_by=user.id)
        assert attendee.event_id == event.id
        assert attendee.user_id == user.id
        assert attendee.seat_id == seat.id
        assert attendee.invited_by == user.id
        db_session.refresh(seat)
        assert seat.status == SeatStatus.ASSIGNED.value

    def test_create_with_seat_no_seat(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        obj_in = EventAttendeeCreate(user_id=user.id)
        attendee = svc.create_with_seat(db_session, obj_in, event_id=event.id, invited_by=user.id)
        assert attendee.event_id == event.id
        assert attendee.user_id == user.id
        assert attendee.seat_id is None

    def test_delete_with_seat_release(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        seat = EventSeat(event_id=event.id, row_label="A", number=1, status=SeatStatus.ASSIGNED.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        att = EventAttendee(event_id=event.id, user_id=user.id, seat_id=seat.id)
        db_session.add(att)
        db_session.commit()
        db_session.refresh(att)
        deleted = svc.delete_with_seat_release(db_session, att.id)
        assert deleted is True
        db_session.refresh(seat)
        assert seat.status == SeatStatus.AVAILABLE.value
        assert svc.get(db_session, att.id) is None

    def test_delete_with_seat_release_not_found(self, db_session):
        svc = EventAttendeeService()
        result = svc.delete_with_seat_release(db_session, 999)
        assert result is False

    def test_delete_with_seat_release_no_seat(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        att = EventAttendee(event_id=event.id, user_id=user.id)
        db_session.add(att)
        db_session.commit()
        db_session.refresh(att)
        deleted = svc.delete_with_seat_release(db_session, att.id)
        assert deleted is True
        assert svc.get(db_session, att.id) is None

    def test_assign_vip_with_seat(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        seat = EventSeat(event_id=event.id, row_label="VIP", number=1, status=SeatStatus.AVAILABLE.value)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)
        attendee = svc.assign_vip(db_session, event.id, user.id, invited_by=user.id, seat_id=seat.id)
        assert attendee.event_id == event.id
        assert attendee.user_id == user.id
        assert attendee.seat_id == seat.id
        assert attendee.status == AttendeeStatus.REGISTERED.value
        db_session.refresh(seat)
        assert seat.status == SeatStatus.ASSIGNED.value

    def test_assign_vip_without_seat(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        attendee = svc.assign_vip(db_session, event.id, user.id, invited_by=user.id)
        assert attendee.event_id == event.id
        assert attendee.user_id == user.id
        assert attendee.seat_id is None
        assert attendee.status == AttendeeStatus.REGISTERED.value

    def test_assign_vip_is_hidden(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        attendee = svc.assign_vip(db_session, event.id, user.id, invited_by=user.id, is_hidden=True)
        assert attendee.is_hidden is True

    def test_check_in(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        att = EventAttendee(event_id=event.id, user_id=user.id, status=AttendeeStatus.REGISTERED.value)
        db_session.add(att)
        db_session.commit()
        db_session.refresh(att)
        result = svc.check_in(db_session, att.id)
        assert result is not None
        assert result.status == AttendeeStatus.ATTENDED.value
        assert result.checked_in_at is not None

    def test_check_in_not_found(self, db_session):
        svc = EventAttendeeService()
        result = svc.check_in(db_session, 999)
        assert result is None

    def test_get_attendee_counts(self, db_session, create_festival, create_event, create_user):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        user = create_user()
        atts = [
            EventAttendee(event_id=event.id, user_id=user.id, status=AttendeeStatus.REGISTERED.value),
            EventAttendee(event_id=event.id, user_id=user.id, status=AttendeeStatus.REGISTERED.value),
            EventAttendee(event_id=event.id, user_id=user.id, status=AttendeeStatus.ATTENDED.value),
            EventAttendee(event_id=event.id, user_id=user.id, status=AttendeeStatus.NO_SHOW.value),
        ]
        for a in atts:
            db_session.add(a)
        db_session.commit()
        counts = svc.get_attendee_counts(db_session, event.id)
        assert counts["total"] == 4
        assert counts["registered"] == 2
        assert counts["attended"] == 1
        assert counts["no_show"] == 1

    def test_get_attendee_counts_empty(self, db_session, create_festival, create_event):
        svc = EventAttendeeService()
        festival = create_festival()
        event = create_event(festival_id=festival.id)
        counts = svc.get_attendee_counts(db_session, event.id)
        assert counts["total"] == 0
        assert counts["registered"] == 0
        assert counts["attended"] == 0
        assert counts["no_show"] == 0
