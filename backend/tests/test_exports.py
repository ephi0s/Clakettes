"""Tests for CSV, ICS, and PDF export endpoints."""

from datetime import datetime, timedelta, timezone

from app.models.event import Event, EventAttendee, EventTicketType
from app.models.festival import Festival
from app.models.registration import FestivalRegistration, RegistrationStatus


def _create_festival(db_session, name="Export Fest"):
    fest = Festival(name=name, is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    return fest


def _create_event(db_session, festival, title="Test Event", with_end_date=True):
    start = datetime(2026, 9, 1, 18, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    event = Event(
        festival_id=festival.id,
        title=title,
        event_type="screening",
        start_date=start,
        end_date=end if with_end_date else None,
        location="Main Hall",
        venue="Cine Clakettes",
        short_description="Short description",
        description="Long description",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def _create_ticket_type(db_session, event, name="General"):
    tt = EventTicketType(event_id=event.id, name=name)
    db_session.add(tt)
    db_session.commit()
    db_session.refresh(tt)
    return tt


def _create_attendee(db_session, event, user=None, ticket_type=None, guest_name=None, guest_email=None):
    att = EventAttendee(
        event_id=event.id,
        user_id=user.id if user else None,
        ticket_type_id=ticket_type.id if ticket_type else None,
        is_guest=user is None,
        guest_name=guest_name,
        guest_email=guest_email,
    )
    db_session.add(att)
    db_session.commit()
    db_session.refresh(att)
    return att


# ========================================================================
# Registrations CSV
# ========================================================================


class TestExportRegistrationsCsv:
    def test_success(self, client, admin_headers, db_session):
        headers, user = admin_headers
        fest = _create_festival(db_session)
        reg = FestivalRegistration(user_id=user.id, festival_id=fest.id, notes="Some notes")
        db_session.add(reg)
        db_session.commit()
        resp = client.get(f"/api/festivals/{fest.id}/registrations/export/csv", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert resp.headers["content-disposition"] == "attachment; filename=registrations.csv"
        content = resp.content.decode("utf-8-sig")
        assert "id,username,full_name,email,status,created_at,notes" in content
        assert "Test User" in content
        assert RegistrationStatus.PENDING.value in content

    def test_requires_auth(self, client, db_session):
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/registrations/export/csv")
        assert resp.status_code == 401

    def test_forbidden_for_non_admin(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/registrations/export/csv", headers=headers)
        assert resp.status_code == 403

    def test_festival_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        resp = client.get("/api/festivals/9999/registrations/export/csv", headers=headers)
        assert resp.status_code == 404


# ========================================================================
# Registrations PDF
# ========================================================================


class TestExportRegistrationsPdf:
    def test_success(self, client, admin_headers, db_session):
        headers, user = admin_headers
        fest = _create_festival(db_session)
        reg = FestivalRegistration(user_id=user.id, festival_id=fest.id)
        db_session.add(reg)
        db_session.commit()
        resp = client.get(f"/api/festivals/{fest.id}/registrations/export/pdf", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("application/pdf")
        assert resp.headers["content-disposition"] == "attachment; filename=registrations.pdf"
        assert resp.content.startswith(b"%PDF")

    def test_requires_auth(self, client, db_session):
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/registrations/export/pdf")
        assert resp.status_code == 401

    def test_forbidden_for_non_admin(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/registrations/export/pdf", headers=headers)
        assert resp.status_code == 403

    def test_festival_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        resp = client.get("/api/festivals/9999/registrations/export/pdf", headers=headers)
        assert resp.status_code == 404


# ========================================================================
# Attendees CSV
# ========================================================================


class TestExportAttendeesCsv:
    def test_success(self, client, admin_headers, db_session):
        headers, user = admin_headers
        fest = _create_festival(db_session)
        event = _create_event(db_session, fest)
        tt = _create_ticket_type(db_session, event, name="VIP")
        _create_attendee(db_session, event, user=user, ticket_type=tt)
        _create_attendee(db_session, event, guest_name="John Doe", guest_email="john@example.com")
        resp = client.get(f"/api/events/{event.id}/attendees/export/csv", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert resp.headers["content-disposition"] == "attachment; filename=attendees.csv"
        content = resp.content.decode("utf-8-sig")
        assert "id,user,guest_name,email,ticket_type,status,checked_in_at" in content
        assert "admin" in content
        assert "VIP" in content
        assert "John Doe" in content
        assert "john@example.com" in content

    def test_requires_auth(self, client, db_session):
        fest = _create_festival(db_session)
        event = _create_event(db_session, fest)
        resp = client.get(f"/api/events/{event.id}/attendees/export/csv")
        assert resp.status_code == 401

    def test_forbidden_for_non_admin(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = _create_festival(db_session)
        event = _create_event(db_session, fest)
        resp = client.get(f"/api/events/{event.id}/attendees/export/csv", headers=headers)
        assert resp.status_code == 403

    def test_event_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        resp = client.get("/api/events/9999/attendees/export/csv", headers=headers)
        assert resp.status_code == 404


# ========================================================================
# Events ICS
# ========================================================================


class TestExportEventsIcs:
    def test_success(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = _create_festival(db_session)
        event = _create_event(db_session, fest, title="Opening Gala")
        resp = client.get(f"/api/festivals/{fest.id}/events/export/ics", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/calendar")
        assert resp.headers["content-disposition"] == "attachment; filename=calendar.ics"
        content = resp.text
        assert "BEGIN:VCALENDAR" in content
        assert "BEGIN:VEVENT" in content
        assert "SUMMARY:Opening Gala" in content
        assert f"UID:event-{event.id}@clakettes" in content
        assert "END:VEVENT" in content
        assert "END:VCALENDAR" in content

    def test_requires_auth(self, client, db_session):
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/events/export/ics")
        assert resp.status_code == 401

    def test_forbidden_for_non_admin(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/events/export/ics", headers=headers)
        assert resp.status_code == 403

    def test_festival_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        resp = client.get("/api/festivals/9999/events/export/ics", headers=headers)
        assert resp.status_code == 404
