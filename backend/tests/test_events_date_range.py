"""Tests for the date-range filter on the events list endpoint."""


def _create_festival(db_session):
    from app.models.festival import Festival

    fest = Festival(name="Test Festival", is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    return fest


def _event_payload(festival_id, title, start_date):
    return {
        "festival_id": festival_id,
        "title": title,
        "start_date": start_date,
        "event_type": "screening",
    }


class TestListEventsDateRange:
    def _create_events(self, client, db_session, admin_headers):
        fest = _create_festival(db_session)
        h, _ = admin_headers
        client.post(
            f"/api/festivals/{fest.id}/events/",
            json=_event_payload(fest.id, "July Event", "2026-07-01T10:00:00"),
            headers=h,
        )
        client.post(
            f"/api/festivals/{fest.id}/events/",
            json=_event_payload(fest.id, "August Event", "2026-08-15T10:00:00"),
            headers=h,
        )
        return fest

    def test_filter_by_date_range(self, client, db_session, admin_headers):
        fest = self._create_events(client, db_session, admin_headers)
        resp = client.get(
            f"/api/festivals/{fest.id}/events/?start_date_from=2026-07-01T00:00:00&start_date_to=2026-07-31T23:59:59"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "July Event"

    def test_no_params_returns_all(self, client, db_session, admin_headers):
        fest = self._create_events(client, db_session, admin_headers)
        resp = client.get(f"/api/festivals/{fest.id}/events/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_without_token_still_allowed(self, client, db_session, admin_headers):
        fest = self._create_events(client, db_session, admin_headers)
        resp = client.get(
            f"/api/festivals/{fest.id}/events/?start_date_from=2026-08-01T00:00:00&start_date_to=2026-08-31T00:00:00"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "August Event"
