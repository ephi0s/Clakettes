"""Tests for jury notes, minutes and annotations on event screenings."""

from datetime import datetime, timezone


def _setup(db_session, admin_headers):
    from app.models.festival import Festival
    from app.models.shortfilm import ShortFilm

    _, admin = admin_headers
    festival = Festival(name="Notes Festival", is_active=True)
    db_session.add(festival)
    db_session.commit()
    db_session.refresh(festival)

    films = []
    for i in range(2):
        film = ShortFilm(
            title=f"Film {i}",
            duration=10 + i,
            festival_id=festival.id,
            user_id=admin.id,
        )
        db_session.add(film)
        films.append(film)
    db_session.commit()
    for film in films:
        db_session.refresh(film)

    return festival, films


def _create_event(client, headers, festival_id, shortfilm_ids=()):
    payload = {
        "festival_id": festival_id,
        "title": "Visionado notas",
        "start_date": datetime.now(timezone.utc).isoformat(),
        "event_type": "screening",
        "screening_shortfilm_ids": list(shortfilm_ids),
    }
    resp = client.post(f"/api/festivals/{festival_id}/events/", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


class TestScreeningNotes:
    def test_notes_start_empty(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        data = client.get(f"/api/events/{event['id']}/screenings").json()
        item = data["items"][0]
        assert item["jury_notes"] is None
        assert item["minutes"] is None
        assert item["annotation"] is None
        assert item["annotated_at"] is None

    def test_set_notes_and_minutes(self, client, db_session, admin_headers):
        headers, admin = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        resp = client.put(
            f"/api/events/{event['id']}/screenings/{films[0].id}/notes",
            json={
                "jury_notes": "Fotografía notable, guion irregular",
                "minutes": "Se propone mención especial por fotografía",
                "annotation": "special_mention",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["jury_notes"] == "Fotografía notable, guion irregular"
        assert data["minutes"] == "Se propone mención especial por fotografía"
        assert data["annotation"] == "special_mention"
        assert data["annotated_by"] == admin.id
        assert data["annotated_at"] is not None

        listed = client.get(f"/api/events/{event['id']}/screenings").json()
        item = listed["items"][0]
        assert item["annotation"] == "special_mention"
        assert item["minutes"] == "Se propone mención especial por fotografía"

    def test_clear_notes_resets_annotated_at(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        client.put(
            f"/api/events/{event['id']}/screenings/{films[0].id}/notes",
            json={"jury_notes": "Buena", "annotation": "accesit"},
            headers=headers,
        )
        resp = client.put(
            f"/api/events/{event['id']}/screenings/{films[0].id}/notes",
            json={"jury_notes": None, "minutes": None, "annotation": None},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["jury_notes"] is None
        assert data["annotation"] is None
        assert data["annotated_at"] is None

    def test_reorder_preserves_notes(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id, films[1].id])

        client.put(
            f"/api/events/{event['id']}/screenings/{films[1].id}/notes",
            json={"minutes": "Acta de la obra 1", "annotation": "accesit"},
            headers=headers,
        )
        resp = client.put(
            f"/api/events/{event['id']}/screenings",
            json={"shortfilm_ids": [films[1].id, films[0].id]},
            headers=headers,
        )
        assert resp.status_code == 200

        data = client.get(f"/api/events/{event['id']}/screenings").json()
        assert [i["shortfilm_id"] for i in data["items"]] == [films[1].id, films[0].id]
        assert data["items"][0]["minutes"] == "Acta de la obra 1"
        assert data["items"][0]["annotation"] == "accesit"
        assert data["items"][1]["minutes"] is None

    def test_invalid_annotation_rejected(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        resp = client.put(
            f"/api/events/{event['id']}/screenings/{films[0].id}/notes",
            json={"annotation": "invented"},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_unknown_screening_returns_404(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        resp = client.put(
            f"/api/events/{event['id']}/screenings/{films[1].id}/notes",
            json={"jury_notes": "No existe"},
            headers=headers,
        )
        assert resp.status_code == 404

    def test_requires_festival_admin(self, client, db_session, admin_headers, auth_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        other_headers, _ = auth_headers
        forbidden = client.put(
            f"/api/events/{event['id']}/screenings/{films[0].id}/notes",
            json={"jury_notes": "Intento ajeno"},
            headers=other_headers,
        )
        assert forbidden.status_code == 403

        anonymous = client.put(
            f"/api/events/{event['id']}/screenings/{films[0].id}/notes",
            json={"jury_notes": "Intento anónimo"},
        )
        assert anonymous.status_code == 401
