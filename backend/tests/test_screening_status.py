"""Tests for screening status (cribado) on event screenings."""

from datetime import datetime, timezone


def _setup(db_session, admin_headers):
    from app.models.festival import Festival
    from app.models.shortfilm import ShortFilm

    _, admin = admin_headers
    festival = Festival(name="Screening Festival", is_active=True)
    db_session.add(festival)
    db_session.commit()
    db_session.refresh(festival)

    films = []
    for i in range(3):
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


def _create_event(client, headers, festival_id, shortfilm_ids=(), title="Visionado"):
    payload = {
        "festival_id": festival_id,
        "title": title,
        "start_date": datetime.now(timezone.utc).isoformat(),
        "event_type": "screening",
        "screening_shortfilm_ids": list(shortfilm_ids),
    }
    resp = client.post(f"/api/festivals/{festival_id}/events/", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


class TestScreeningStatus:
    def test_new_screenings_are_pending(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [f.id for f in films])

        resp = client.get(f"/api/events/{event['id']}/screenings")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 3
        assert all(item["status"] == "pending" for item in data["items"])
        assert data["counts_by_status"] == {"pending": 3, "screened": 0, "disqualified": 0}
        assert data["total_duration"] == 33

    def test_disqualify_and_filter(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [f.id for f in films])

        resp = client.patch(
            f"/api/events/{event['id']}/screenings/{films[0].id}",
            json={"status": "disqualified", "status_reason": "Copia defectuosa"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_disqualified"] is True
        assert resp.json()["status_reason"] == "Copia defectuosa"

        by_status = client.get(f"/api/events/{event['id']}/screenings?status=disqualified").json()
        assert [i["shortfilm_id"] for i in by_status["items"]] == [films[0].id]
        assert by_status["counts_by_status"]["disqualified"] == 1
        assert by_status["counts_by_status"]["pending"] == 2

        hidden = client.get(f"/api/events/{event['id']}/screenings?include_disqualified=false").json()
        assert [i["shortfilm_id"] for i in hidden["items"]] == [films[1].id, films[2].id]
        assert hidden["counts_by_status"]["disqualified"] == 1

    def test_reason_cleared_when_not_disqualified(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        client.patch(
            f"/api/events/{event['id']}/screenings/{films[0].id}",
            json={"status": "disqualified", "status_reason": "Motivo"},
            headers=headers,
        )
        resp = client.patch(
            f"/api/events/{event['id']}/screenings/{films[0].id}",
            json={"status": "screened"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "screened"
        assert resp.json()["status_reason"] is None
        assert resp.json()["is_disqualified"] is False

    def test_reorder_preserves_status(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id, films[1].id])

        client.patch(
            f"/api/events/{event['id']}/screenings/{films[1].id}",
            json={"status": "disqualified", "status_reason": "Fuera de bases"},
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
        assert data["items"][0]["status"] == "disqualified"
        assert data["items"][0]["status_reason"] == "Fuera de bases"
        assert data["items"][1]["status"] == "pending"

    def test_invalid_status_rejected(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        resp = client.patch(
            f"/api/events/{event['id']}/screenings/{films[0].id}",
            json={"status": "invented"},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_unknown_screening_returns_404(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        resp = client.patch(
            f"/api/events/{event['id']}/screenings/{films[1].id}",
            json={"status": "screened"},
            headers=headers,
        )
        assert resp.status_code == 404

    def test_filter_by_participant_tag(self, client, db_session, admin_headers):
        from app.models.participant_tag import ParticipantTag
        from app.models.user_role import UserParticipantTag

        headers, admin = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [f.id for f in films])

        student = ParticipantTag(name="student", display_name="Estudiante", category="other")
        resident = ParticipantTag(name="resident", display_name="Residente", category="other")
        db_session.add_all([student, resident])
        db_session.commit()
        db_session.refresh(student)
        db_session.refresh(resident)
        db_session.add(UserParticipantTag(user_id=admin.id, tag_id=student.id, festival_id=festival.id))
        db_session.commit()

        by_tag = client.get(f"/api/events/{event['id']}/screenings?participant_tag_id={student.id}").json()
        assert len(by_tag["items"]) == 3

        by_category = client.get(f"/api/events/{event['id']}/screenings?participant_tag_category=other").json()
        assert len(by_category["items"]) == 3

        other_tag = client.get(f"/api/events/{event['id']}/screenings?participant_tag_id={resident.id}").json()
        assert other_tag["items"] == []

        other_category = client.get(f"/api/events/{event['id']}/screenings?participant_tag_category=acting").json()
        assert other_category["items"] == []

    def test_requires_festival_admin(self, client, db_session, admin_headers, auth_headers):
        headers, _ = admin_headers
        festival, films = _setup(db_session, admin_headers)
        event = _create_event(client, headers, festival.id, [films[0].id])

        other_headers, _ = auth_headers
        resp = client.patch(
            f"/api/events/{event['id']}/screenings/{films[0].id}",
            json={"status": "disqualified"},
            headers=other_headers,
        )
        assert resp.status_code == 403

        anonymous = client.patch(
            f"/api/events/{event['id']}/screenings/{films[0].id}",
            json={"status": "disqualified"},
        )
        assert anonymous.status_code == 401
