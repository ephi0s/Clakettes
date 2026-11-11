"""Tests for participant tag verification (eligibility for special categories)."""

from datetime import datetime, timezone


def _create_festival(db_session, name="Eligibility Festival"):
    from app.models.festival import Festival

    festival = Festival(name=name, is_active=True)
    db_session.add(festival)
    db_session.commit()
    db_session.refresh(festival)
    return festival


def _create_tag(db_session, name="student", display_name="Estudiante", category="other"):
    from app.models.participant_tag import ParticipantTag

    tag = ParticipantTag(name=name, display_name=display_name, category=category)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


def _assign_tag(client, headers, user_id, tag_id, festival_id=None):
    payload = {"user_id": user_id, "tag_id": tag_id, "festival_id": festival_id}
    resp = client.post(f"/api/users/{user_id}/participant-tags/", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def _make_organizer(db_session, user_id, festival_id):
    from app.models.user_festival import user_festival

    db_session.execute(
        user_festival.insert().values(
            user_id=user_id,
            festival_id=festival_id,
            role="organizer",
            joined_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()


class TestTagVerification:
    def test_assignment_starts_unverified(self, client, db_session, admin_headers, create_user):
        headers, _ = admin_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        user, _ = create_user(username="student1", email="student1@example.com")

        data = _assign_tag(client, headers, user.id, tag.id, festival.id)
        assert data["verification_status"] == "unverified"
        assert data["verification_method"] is None
        assert data["verified_at"] is None

    def test_verify_with_external_method(self, client, db_session, admin_headers, create_user):
        headers, admin = admin_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        user, _ = create_user(username="student2", email="student2@example.com")
        assigned = _assign_tag(client, headers, user.id, tag.id, festival.id)

        resp = client.patch(
            f"/api/users/{user.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified", "method": "external", "notes": "Matrícula comprobada en el centro"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["verification_status"] == "verified"
        assert data["verification_method"] == "external"
        assert data["verification_notes"] == "Matrícula comprobada en el centro"
        assert data["verified_by"] == admin.id
        assert data["verified_at"] is not None

    def test_reject_clears_verified_at(self, client, db_session, admin_headers, create_user):
        headers, _ = admin_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        user, _ = create_user(username="student3", email="student3@example.com")
        assigned = _assign_tag(client, headers, user.id, tag.id, festival.id)

        client.patch(
            f"/api/users/{user.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified", "method": "document"},
            headers=headers,
        )
        resp = client.patch(
            f"/api/users/{user.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "rejected", "notes": "Documento caducado"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["verification_status"] == "rejected"
        assert data["verified_at"] is None

    def test_only_festival_organizers_can_verify(self, client, db_session, admin_headers, auth_headers, create_user):
        headers, _ = admin_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        user, _ = create_user(username="student4", email="student4@example.com")
        assigned = _assign_tag(client, headers, user.id, tag.id, festival.id)

        other_headers, _ = auth_headers
        resp = client.patch(
            f"/api/users/{user.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified", "method": "external"},
            headers=other_headers,
        )
        assert resp.status_code == 403

        anonymous = client.patch(
            f"/api/users/{user.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified"},
        )
        assert anonymous.status_code == 401

    def test_festival_organizer_can_verify(self, client, db_session, admin_headers, create_user, auth_headers):
        headers, _ = admin_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        user, _ = create_user(username="student5", email="student5@example.com")
        assigned = _assign_tag(client, headers, user.id, tag.id, festival.id)

        organizer_headers, organizer = auth_headers
        _make_organizer(db_session, organizer.id, festival.id)

        resp = client.patch(
            f"/api/users/{user.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified", "method": "external"},
            headers=organizer_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["verified_by"] == organizer.id

    def test_organizer_can_list_and_filter_by_status(
        self, client, db_session, admin_headers, create_user, auth_headers
    ):
        headers, _ = admin_headers
        festival = _create_festival(db_session)
        student = _create_tag(db_session)
        resident = _create_tag(db_session, name="resident", display_name="Residente")
        user, _ = create_user(username="student6", email="student6@example.com")
        verified = _assign_tag(client, headers, user.id, student.id, festival.id)
        _assign_tag(client, headers, user.id, resident.id, festival.id)
        client.patch(
            f"/api/users/{user.id}/participant-tags/{verified['id']}/verify",
            json={"status": "verified", "method": "external"},
            headers=headers,
        )

        organizer_headers, organizer = auth_headers
        _make_organizer(db_session, organizer.id, festival.id)

        url = f"/api/users/{user.id}/participant-tags/?festival_id={festival.id}"
        forbidden = client.get(url, headers=organizer_headers)
        assert forbidden.status_code == 200
        assert forbidden.json()["total"] == 2

        filtered = client.get(f"{url}&verification_status=verified", headers=organizer_headers)
        assert filtered.status_code == 200
        assert filtered.json()["total"] == 1
        assert filtered.json()["items"][0]["verification_status"] == "verified"

        without_festival = client.get(f"/api/users/{user.id}/participant-tags/", headers=organizer_headers)
        assert without_festival.status_code == 403

    def test_invalid_verification_status(self, client, db_session, admin_headers, create_user):
        headers, _ = admin_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        user, _ = create_user(username="student7", email="student7@example.com")
        assigned = _assign_tag(client, headers, user.id, tag.id, festival.id)

        resp = client.patch(
            f"/api/users/{user.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "invented"},
            headers=headers,
        )
        assert resp.status_code == 422


class TestScreeningVerifiedEligibility:
    def test_screenings_can_require_verified_tags(self, client, db_session, admin_headers, create_user):
        from app.models.shortfilm import ShortFilm

        headers, admin = admin_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        _make_organizer(db_session, admin.id, festival.id)
        film = ShortFilm(title="Eligible Film", duration=12, festival_id=festival.id, user_id=admin.id)
        db_session.add(film)
        db_session.commit()
        db_session.refresh(film)

        event_payload = {
            "festival_id": festival.id,
            "title": "Cribado elegibilidad",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "event_type": "screening",
            "screening_shortfilm_ids": [film.id],
        }
        event = client.post(f"/api/festivals/{festival.id}/events/", json=event_payload, headers=headers).json()

        assigned = _assign_tag(client, headers, admin.id, tag.id, festival.id)
        url = f"/api/events/{event['id']}/screenings?participant_tag_id={tag.id}&participant_tag_verified_only=true"
        assert client.get(url).json()["items"] == []

        client.patch(
            f"/api/users/{admin.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified", "method": "external"},
            headers=headers,
        )
        assert len(client.get(url).json()["items"]) == 1
