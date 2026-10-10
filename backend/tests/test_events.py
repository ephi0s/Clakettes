"""Tests for event/gala endpoints — events, ticket types, seats, reservations, attendees, awards."""

from datetime import datetime, timezone


def _create_festival(db_session):
    from app.models.festival import Festival

    fest = Festival(name="Test Festival", is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    return fest


def _event_payload(festival_id, title="Test Event", event_type="screening"):
    return {
        "festival_id": festival_id,
        "title": title,
        "start_date": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
    }


# ========================================================================
# Events
# ========================================================================


class TestListEvents:
    def test_list_empty(self, client, db_session):
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/events/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_data(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id, "E1"), headers=h)
        client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id, "E2"), headers=h)
        resp = client.get(f"/api/festivals/{fest.id}/events/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_festival_not_found(self, client):
        resp = client.get("/api/festivals/9999/events/")
        assert resp.status_code == 404

    def test_list_pagination(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        for i in range(5):
            client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id, f"E{i}"), headers=h)
        resp = client.get(f"/api/festivals/{fest.id}/events/?page=1&size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 2

    def test_list_filter_active(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id, "Active"), headers=h)
        e2 = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id, "Inactive"), headers=h)
        e2_id = e2.json()["id"]
        client.put(f"/api/events/{e2_id}", json={"is_active": False}, headers=h)
        resp = client.get(f"/api/festivals/{fest.id}/events/?is_active=true")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    def test_list_filter_event_type(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id, "Gala", "gala"), headers=h)
        client.post(
            f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id, "Workshop", "workshop"), headers=h
        )  # noqa: E501
        resp = client.get(f"/api/festivals/{fest.id}/events/?event_type=gala")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1


class TestCreateEvent:
    def test_create_success(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        resp = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test Event"
        assert data["event_type"] == "screening"
        assert data["is_active"] is True

    def test_create_requires_auth(self, client, db_session):
        fest = _create_festival(db_session)
        resp = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id))
        assert resp.status_code == 401

    def test_create_festival_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.post("/api/festivals/9999/events/", json=_event_payload(9999), headers=h)
        assert resp.status_code == 404


class TestGetEvent:
    def test_get_success(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/events/{eid}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test Event"

    def test_get_not_found(self, client):
        resp = client.get("/api/events/9999")
        assert resp.status_code == 404


class TestUpdateEvent:
    def test_update_success(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.put(f"/api/events/{eid}", json={"title": "Updated"}, headers=h)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    def test_update_requires_auth(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.put(f"/api/events/{eid}", json={"title": "Hacked"})
        assert resp.status_code == 401

    def test_update_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.put("/api/events/9999", json={"title": "Ghost"}, headers=h)
        assert resp.status_code == 404


class TestDeleteEvent:
    def test_delete_success(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.delete(f"/api/events/{eid}", headers=h)
        assert resp.status_code == 200
        assert client.get(f"/api/events/{eid}").status_code == 404

    def test_delete_requires_auth(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.delete(f"/api/events/{eid}")
        assert resp.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.delete("/api/events/9999", headers=h)
        assert resp.status_code == 404


# ========================================================================
# Ticket Types
# ========================================================================


class TestListTicketTypes:
    def test_list_empty(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/events/{eid}/ticket-types/")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_list_with_data(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "VIP",
                "price": 50.0,
            },
            headers=h,
        )
        client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "General",
                "price": 20.0,
            },
            headers=h,
        )
        resp = client.get(f"/api/events/{eid}/ticket-types/")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 2

    def test_list_event_not_found(self, client):
        resp = client.get("/api/events/9999/ticket-types/")
        assert resp.status_code == 404


class TestCreateTicketType:
    def test_create_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "General",
                "price": 15.0,
                "capacity": 100,
            },
            headers=h,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "General"
        assert data["price"] == 15.0
        assert data["capacity"] == 100

    def test_create_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "No Auth",
                "price": 0,
            },
        )
        assert resp.status_code == 401

    def test_create_event_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.post(
            "/api/events/9999/ticket-types/",
            json={
                "event_id": 9999,
                "name": "Ghost",
                "price": 0,
            },
            headers=h,
        )
        assert resp.status_code == 404


class TestUpdateTicketType:
    def test_update_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        tt = client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "Old",
                "price": 10,
            },
            headers=h,
        )
        tt_id = tt.json()["id"]
        resp = client.put(f"/api/ticket-types/{tt_id}", json={"name": "Updated", "price": 25}, headers=h)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"
        assert resp.json()["price"] == 25

    def test_update_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        tt = client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "Old",
                "price": 10,
            },
            headers=h,
        )
        tt_id = tt.json()["id"]
        resp = client.put(f"/api/ticket-types/{tt_id}", json={"name": "Hacked"})
        assert resp.status_code == 401

    def test_update_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.put("/api/ticket-types/9999", json={"name": "Ghost"}, headers=h)
        assert resp.status_code == 404


class TestDeleteTicketType:
    def test_delete_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        tt = client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "Delete Me",
                "price": 5,
            },
            headers=h,
        )
        tt_id = tt.json()["id"]
        resp = client.delete(f"/api/ticket-types/{tt_id}", headers=h)
        assert resp.status_code == 200

    def test_delete_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        tt = client.post(
            f"/api/events/{eid}/ticket-types/",
            json={
                "event_id": eid,
                "name": "No Auth",
                "price": 5,
            },
            headers=h,
        )
        tt_id = tt.json()["id"]
        resp = client.delete(f"/api/ticket-types/{tt_id}")
        assert resp.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.delete("/api/ticket-types/9999", headers=h)
        assert resp.status_code == 404


# ========================================================================
# Seats
# ========================================================================


class TestListSeats:
    def test_list_empty(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/events/{eid}/seats/")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_list_with_data(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1", "2"],
                "numbers_per_row": 2,
            },
            headers=h,
        )
        resp = client.get(f"/api/events/{eid}/seats/")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 4

    def test_list_filter_section(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "VIP",
                "rows": ["A"],
                "numbers_per_row": 2,
            },
            headers=h,
        )
        client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "General",
                "rows": ["B"],
                "numbers_per_row": 2,
            },
            headers=h,
        )
        resp = client.get(f"/api/events/{eid}/seats/?section=VIP")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 2


class TestBulkCreateSeats:
    def test_bulk_create_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "Main",
                "rows": ["A", "B", "C"],
                "numbers_per_row": 5,
            },
            headers=h,
        )
        assert resp.status_code == 201
        assert len(resp.json()) == 15

    def test_bulk_create_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "Main",
                "rows": ["A"],
                "numbers_per_row": 2,
            },
        )
        assert resp.status_code == 401

    def test_bulk_create_event_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.post(
            "/api/events/9999/seats/bulk",
            json={
                "section": "X",
                "rows": ["A"],
                "numbers_per_row": 2,
            },
            headers=h,
        )
        assert resp.status_code == 404


class TestListSeatSections:
    def test_sections(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "VIP",
                "rows": ["A"],
                "numbers_per_row": 2,
            },
            headers=h,
        )
        client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "General",
                "rows": ["B"],
                "numbers_per_row": 2,
            },
            headers=h,
        )
        resp = client.get(f"/api/events/{eid}/seats/sections")
        assert resp.status_code == 200
        assert set(resp.json()) == {"VIP", "General"}

    def test_sections_event_not_found(self, client):
        resp = client.get("/api/events/9999/seats/sections")
        assert resp.status_code == 404


class TestGetSeatCounts:
    def test_counts(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 10,
            },
            headers=h,
        )
        resp = client.get(f"/api/events/{eid}/seats/counts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 10
        assert data["available"] == 10
        assert data["occupied"] == 0

    def test_counts_event_not_found(self, client):
        resp = client.get("/api/events/9999/seats/counts")
        assert resp.status_code == 404


class TestUpdateSeat:
    def test_update_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.put(f"/api/seats/{seat_id}", json={"notes": "VIP seat"}, headers=h)
        assert resp.status_code == 200
        assert resp.json()["notes"] == "VIP seat"

    def test_update_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.put(f"/api/seats/{seat_id}", json={"notes": "Hacked"})
        assert resp.status_code == 401

    def test_update_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.put("/api/seats/9999", json={"notes": "Ghost"}, headers=h)
        assert resp.status_code == 404


class TestReleaseSeat:
    def test_release_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        client.put(f"/api/seats/{seat_id}", json={"status": "assigned"}, headers=h)
        resp = client.post(f"/api/seats/{seat_id}/release", headers=h)
        assert resp.status_code == 200

    def test_release_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.post(f"/api/seats/{seat_id}/release")
        assert resp.status_code == 401

    def test_release_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.post("/api/seats/9999/release", headers=h)
        assert resp.status_code == 404


class TestDeleteSeat:
    def test_delete_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.delete(f"/api/seats/{seat_id}", headers=h)
        assert resp.status_code == 200

    def test_delete_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.delete(f"/api/seats/{seat_id}")
        assert resp.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.delete("/api/seats/9999", headers=h)
        assert resp.status_code == 404


# ========================================================================
# Reservations
# ========================================================================


class TestCreateReservation:
    def test_create_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["event_id"] == eid

    def test_create_with_seat(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id, "seat_id": seat_id}],
            },
            headers=h,
        )
        assert resp.status_code == 201

    def test_create_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(f"/api/events/{eid}/reservations/", json={"event_id": eid})
        assert resp.status_code == 401


class TestListReservations:
    def test_list(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        )
        resp = client.get(f"/api/events/{eid}/reservations/", headers=h)
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    def test_list_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/events/{eid}/reservations/")
        assert resp.status_code == 401

    def test_list_event_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.get("/api/events/9999/reservations/", headers=h)
        assert resp.status_code == 404


class TestUpdateReservation:
    def test_update_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.put(f"/api/reservations/{rid}", json={"notes": "Updated notes"}, headers=h)
        assert resp.status_code == 200
        assert resp.json()["notes"] == "Updated notes"

    def test_update_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.put(f"/api/reservations/{rid}", json={"notes": "Hacked"})
        assert resp.status_code == 401

    def test_update_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.put("/api/reservations/9999", json={"notes": "Ghost"}, headers=h)
        assert resp.status_code == 404


class TestConfirmReservation:
    def test_confirm_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.post(f"/api/reservations/{rid}/confirm", headers=h)
        assert resp.status_code == 200
        assert resp.json()["reservation"]["status"] == "confirmed"

    def test_confirm_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.post(f"/api/reservations/{rid}/confirm")
        assert resp.status_code == 401


class TestCancelReservation:
    def test_cancel_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.post(f"/api/reservations/{rid}/cancel", headers=h)
        assert resp.status_code == 200
        assert resp.json()["reservation"]["status"] == "cancelled"

    def test_cancel_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.post(f"/api/reservations/{rid}/cancel")
        assert resp.status_code == 401


class TestDeleteReservation:
    def test_delete_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.delete(f"/api/reservations/{rid}", headers=h)
        assert resp.status_code == 200

    def test_delete_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        res = client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        ).json()
        rid = res["id"]
        resp = client.delete(f"/api/reservations/{rid}")
        assert resp.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.delete("/api/reservations/9999", headers=h)
        assert resp.status_code == 404


# ========================================================================
# Attendees
# ========================================================================


class TestCreateAttendee:
    def test_create_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/attendees/",
            json={
                "user_id": user.id,
            },
            headers=h,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "registered"
        assert data["event_id"] == eid

    def test_create_with_seat(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "A",
                "rows": ["1"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.post(
            f"/api/events/{eid}/attendees/",
            json={
                "user_id": user.id,
                "seat_id": seat_id,
            },
            headers=h,
        )
        assert resp.status_code == 201

    def test_create_guest(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/attendees/",
            json={
                "is_guest": True,
                "guest_name": "John Doe",
                "guest_email": "john@example.com",
            },
            headers=h,
        )
        assert resp.status_code == 201
        assert resp.json()["guest_name"] == "John Doe"

    def test_create_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id})
        assert resp.status_code == 401

    def test_create_event_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.post("/api/events/9999/attendees/", json={"user_id": 1}, headers=h)
        assert resp.status_code == 404

    def test_create_seat_not_found(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(
            f"/api/events/{eid}/attendees/",
            json={
                "user_id": user.id,
                "seat_id": 9999,
            },
            headers=h,
        )
        assert resp.status_code == 404


class TestListAttendees:
    def test_list_empty(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/events/{eid}/attendees/", headers=h)
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_list_with_data(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h)
        resp = client.get(f"/api/events/{eid}/attendees/", headers=h)
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    def test_list_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/events/{eid}/attendees/")
        assert resp.status_code == 401


class TestGetAttendee:
    def test_get_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        resp = client.get(f"/api/attendees/{att['id']}")
        assert resp.status_code == 200
        assert resp.json()["event_id"] == eid

    def test_get_not_found(self, client):
        resp = client.get("/api/attendees/9999")
        assert resp.status_code == 404


class TestUpdateAttendee:
    def test_update_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        resp = client.put(f"/api/attendees/{att['id']}", json={"notes": "VIP guest"}, headers=h)
        assert resp.status_code == 200
        assert resp.json()["notes"] == "VIP guest"

    def test_update_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        resp = client.put(f"/api/attendees/{att['id']}", json={"notes": "Hacked"})
        assert resp.status_code == 401

    def test_update_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.put("/api/attendees/9999", json={"notes": "Ghost"}, headers=h)
        assert resp.status_code == 404


class TestCheckInAttendee:
    def test_check_in_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        resp = client.post(f"/api/attendees/{att['id']}/check-in", headers=h)
        assert resp.status_code == 200
        assert resp.json()["attendee"]["status"] == "attended"

    def test_check_in_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        resp = client.post(f"/api/attendees/{att['id']}/check-in")
        assert resp.status_code == 401

    def test_check_in_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.post("/api/attendees/9999/check-in", headers=h)
        assert resp.status_code == 404


class TestAttendeeCounts:
    def test_counts(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        client.post(f"/api/attendees/{att['id']}/check-in", headers=h)
        resp = client.get(f"/api/events/{eid}/attendees/counts", headers=h)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["attended"] == 1

    def test_counts_event_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.get("/api/events/9999/attendees/counts", headers=h)
        assert resp.status_code == 404


class TestDeleteAttendee:
    def test_delete_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        resp = client.delete(f"/api/attendees/{att['id']}", headers=h)
        assert resp.status_code == 200

    def test_delete_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        att = client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h).json()
        resp = client.delete(f"/api/attendees/{att['id']}")
        assert resp.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.delete("/api/attendees/9999", headers=h)
        assert resp.status_code == 404


# ========================================================================
# VIP Assignment
# ========================================================================


class TestAssignVIP:
    def test_assign_vip_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(f"/api/events/{eid}/assign-vip?user_id={user.id}", headers=h)
        assert resp.status_code == 201
        assert resp.json()["user_id"] == user.id

    def test_assign_vip_with_seat(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={
                "section": "VIP",
                "rows": ["A"],
                "numbers_per_row": 1,
            },
            headers=h,
        ).json()
        seat_id = seats[0]["id"]
        resp = client.post(f"/api/events/{eid}/assign-vip?user_id={user.id}&seat_id={seat_id}", headers=h)
        assert resp.status_code == 201

    def test_assign_vip_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(f"/api/events/{eid}/assign-vip?user_id={user.id}")
        assert resp.status_code == 401

    def test_assign_vip_event_not_found(self, client, admin_headers):
        h, user = admin_headers
        resp = client.post(f"/api/events/9999/assign-vip?user_id={user.id}", headers=h)
        assert resp.status_code == 404

    def test_assign_vip_user_not_found(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(f"/api/events/{eid}/assign-vip?user_id=9999", headers=h)
        assert resp.status_code == 404

    def test_assign_vip_hidden(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.post(f"/api/events/{eid}/assign-vip?user_id={user.id}&is_hidden=true", headers=h)
        assert resp.status_code == 201
        assert resp.json()["is_hidden"] is True


# ========================================================================
# My Events & My Reservation
# ========================================================================


class TestMyEvents:
    def test_empty(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.get("/api/users/me/events/", headers=h)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_data(self, client, db_session, admin_headers):
        h, user = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(f"/api/events/{eid}/attendees/", json={"user_id": user.id}, headers=h)
        resp = client.get("/api/users/me/events/", headers=h)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_requires_auth(self, client):
        resp = client.get("/api/users/me/events/")
        assert resp.status_code == 401


class TestMyReservation:
    def test_get_my_reservation(self, client, db_session, admin_headers):
        h, user = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        client.post(
            f"/api/events/{eid}/reservations/",
            json={
                "event_id": eid,
                "attendees": [{"user_id": user.id}],
            },
            headers=h,
        )
        resp = client.get(f"/api/users/me/events/{eid}/reservation", headers=h)
        assert resp.status_code == 200
        assert resp.json()["event_id"] == eid

    def test_not_found(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/users/me/events/{eid}/reservation", headers=h)
        assert resp.status_code == 404

    def test_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h)
        eid = created.json()["id"]
        resp = client.get(f"/api/users/me/events/{eid}/reservation")
        assert resp.status_code == 401


# ========================================================================
# Awards
# ========================================================================


class TestListFestivalAwards:
    def test_list_empty(self, client, db_session):
        fest = _create_festival(db_session)
        resp = client.get(f"/api/festivals/{fest.id}/awards/")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_list_with_data(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "user_id": user.id,
                "award_name": "Best Director",
                "award_category": "Main",
            },
            headers=h,
        )
        client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "Best Film",
                "award_category": "Main",
                "position": 1,
            },
            headers=h,
        )
        resp = client.get(f"/api/festivals/{fest.id}/awards/")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 2

    def test_list_festival_not_found(self, client):
        resp = client.get("/api/festivals/9999/awards/")
        assert resp.status_code == 404

    def test_list_filter_user(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "user_id": user.id,
                "award_name": "My Award",
            },
            headers=h,
        )
        client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "Other Award",
            },
            headers=h,
        )
        resp = client.get(f"/api/festivals/{fest.id}/awards/?user_id={user.id}")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    def test_list_pagination(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        for i in range(5):
            client.post(
                f"/api/festivals/{fest.id}/awards/",
                json={
                    "festival_id": fest.id,
                    "award_name": f"Award {i}",
                },
                headers=h,
            )
        resp = client.get(f"/api/festivals/{fest.id}/awards/?page=1&size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5


class TestCreateAward:
    def test_create_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        resp = client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "Best Short Film",
                "award_category": "Competition",
                "year": 2026,
                "is_winner": True,
            },
            headers=h,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["award_name"] == "Best Short Film"
        assert data["year"] == 2026
        assert data["is_verified"] is False

    def test_create_requires_auth(self, client, db_session):
        fest = _create_festival(db_session)
        resp = client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "No Auth",
            },
        )
        assert resp.status_code == 401

    def test_create_festival_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.post(
            "/api/festivals/9999/awards/",
            json={
                "festival_id": 9999,
                "award_name": "Ghost Award",
            },
            headers=h,
        )
        assert resp.status_code == 404


class TestUpdateAward:
    def test_update_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "Old Name",
            },
            headers=h,
        ).json()
        aid = created["id"]
        resp = client.put(
            f"/api/awards/{aid}",
            json={
                "award_name": "Updated Name",
            },
            headers=h,
        )
        assert resp.status_code == 200
        assert resp.json()["award_name"] == "Updated Name"

    def test_update_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "Old",
            },
            headers=h,
        ).json()
        aid = created["id"]
        resp = client.put(f"/api/awards/{aid}", json={"award_name": "Hacked"})
        assert resp.status_code == 401

    def test_update_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.put("/api/awards/9999", json={"award_name": "Ghost"}, headers=h)
        assert resp.status_code == 404


class TestDeleteAward:
    def test_delete_success(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "Delete Me",
            },
            headers=h,
        ).json()
        aid = created["id"]
        resp = client.delete(f"/api/awards/{aid}", headers=h)
        assert resp.status_code == 200

    def test_delete_requires_auth(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        created = client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "award_name": "No Auth",
            },
            headers=h,
        ).json()
        aid = created["id"]
        resp = client.delete(f"/api/awards/{aid}")
        assert resp.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        h, _ = admin_headers
        resp = client.delete("/api/awards/9999", headers=h)
        assert resp.status_code == 404


class TestListUserAwards:
    def test_list_empty(self, client, db_session):
        _create_festival(db_session)
        from app.services.user_service import UserService

        svc = UserService()
        from app.schemas.user import UserCreate

        u = svc.create(
            db_session,
            UserCreate(
                username="awarduser",
                email="award@example.com",
                full_name="Award User",
                role="user",
                password="Test1234",
            ),
        )
        resp = client.get(f"/api/users/{u.id}/awards/")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_list_with_data(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, user = admin_headers
        client.post(
            f"/api/festivals/{fest.id}/awards/",
            json={
                "festival_id": fest.id,
                "user_id": user.id,
                "award_name": "Best Actor",
                "is_public": True,
            },
            headers=h,
        )
        resp = client.get(f"/api/users/{user.id}/awards/")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    def test_list_user_not_found(self, client):
        resp = client.get("/api/users/9999/awards/")
        assert resp.status_code == 404
