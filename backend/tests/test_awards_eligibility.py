"""Tests for award eligibility criteria and recipient verification."""

from datetime import datetime, timezone


def _create_festival(db_session, name="Awards Festival"):
    from app.models.festival import Festival

    festival = Festival(name=name, is_active=True)
    db_session.add(festival)
    db_session.commit()
    db_session.refresh(festival)
    return festival


def _create_film(db_session, user_id, festival_id, title="Award Film"):
    from app.models.shortfilm import ShortFilm

    film = ShortFilm(title=title, duration=10, festival_id=festival_id, user_id=user_id)
    db_session.add(film)
    db_session.commit()
    db_session.refresh(film)
    return film


def _award_payload(festival_id, film_id, tags=None, name="Best Short Film"):
    return {
        "festival_id": festival_id,
        "shortfilm_id": film_id,
        "award_name": name,
        "eligibility_tags": tags or [],
        "year": datetime.now(timezone.utc).year,
    }


class TestAwardEligibility:
    def test_create_with_eligibility_tags(self, client, db_session, admin_headers):
        headers, admin = admin_headers
        festival = _create_festival(db_session)
        film = _create_film(db_session, admin.id, festival.id)

        resp = client.post(
            f"/api/festivals/{festival.id}/awards/",
            json=_award_payload(festival.id, film.id, ["student", "resident"]),
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["eligibility_tags"] == ["student", "resident"]
        assert data["recipient_verified"] is False
        assert data["recipient_verified_at"] is None

    def test_update_eligibility_tags(self, client, db_session, admin_headers):
        headers, admin = admin_headers
        festival = _create_festival(db_session)
        film = _create_film(db_session, admin.id, festival.id)
        award = client.post(
            f"/api/festivals/{festival.id}/awards/",
            json=_award_payload(festival.id, film.id, ["student"]),
            headers=headers,
        ).json()

        resp = client.put(f"/api/awards/{award['id']}", json={"eligibility_tags": ["resident"]}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["eligibility_tags"] == ["resident"]
        assert resp.json()["award_name"] == "Best Short Film"

    def test_filter_by_eligibility_tag_and_verification(self, client, db_session, admin_headers):
        headers, admin = admin_headers
        festival = _create_festival(db_session)
        film = _create_film(db_session, admin.id, festival.id)
        student = client.post(
            f"/api/festivals/{festival.id}/awards/",
            json=_award_payload(festival.id, film.id, ["student"], name="Student Award"),
            headers=headers,
        ).json()
        client.post(
            f"/api/festivals/{festival.id}/awards/",
            json=_award_payload(festival.id, film.id, ["resident"], name="Resident Award"),
            headers=headers,
        )
        client.patch(
            f"/api/awards/{student['id']}/recipient-verification",
            json={"verified": True, "notes": "Matrícula en vigor"},
            headers=headers,
        )

        by_tag = client.get(f"/api/festivals/{festival.id}/awards/?eligibility_tag=student").json()
        assert by_tag["total"] == 1
        assert by_tag["items"][0]["award_name"] == "Student Award"

        verified = client.get(f"/api/festivals/{festival.id}/awards/?recipient_verified=true").json()
        assert verified["total"] == 1

        pending = client.get(f"/api/festivals/{festival.id}/awards/?recipient_verified=false").json()
        assert pending["total"] == 1
        assert pending["items"][0]["award_name"] == "Resident Award"

    def test_verify_and_unverify_recipient(self, client, db_session, admin_headers):
        headers, admin = admin_headers
        festival = _create_festival(db_session)
        film = _create_film(db_session, admin.id, festival.id)
        award = client.post(
            f"/api/festivals/{festival.id}/awards/",
            json=_award_payload(festival.id, film.id, ["student"]),
            headers=headers,
        ).json()

        resp = client.patch(
            f"/api/awards/{award['id']}/recipient-verification",
            json={"verified": True, "notes": "Certificado revisado"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["recipient_verified"] is True
        assert data["recipient_verified_by"] == admin.id
        assert data["recipient_verified_at"] is not None
        assert data["recipient_verification_notes"] == "Certificado revisado"

        resp = client.patch(
            f"/api/awards/{award['id']}/recipient-verification",
            json={"verified": False},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["recipient_verified"] is False
        assert resp.json()["recipient_verified_at"] is None

    def test_verification_requires_festival_admin(self, client, db_session, admin_headers, auth_headers):
        headers, admin = admin_headers
        festival = _create_festival(db_session)
        film = _create_film(db_session, admin.id, festival.id)
        award = client.post(
            f"/api/festivals/{festival.id}/awards/",
            json=_award_payload(festival.id, film.id),
            headers=headers,
        ).json()

        other_headers, _ = auth_headers
        forbidden = client.patch(
            f"/api/awards/{award['id']}/recipient-verification",
            json={"verified": True},
            headers=other_headers,
        )
        assert forbidden.status_code == 403

        anonymous = client.patch(
            f"/api/awards/{award['id']}/recipient-verification",
            json={"verified": True},
        )
        assert anonymous.status_code == 401

        missing = client.patch(
            "/api/awards/9999/recipient-verification",
            json={"verified": True},
            headers=headers,
        )
        assert missing.status_code == 404

    def test_invalid_verification_body(self, client, db_session, admin_headers):
        headers, admin = admin_headers
        festival = _create_festival(db_session)
        film = _create_film(db_session, admin.id, festival.id)
        award = client.post(
            f"/api/festivals/{festival.id}/awards/",
            json=_award_payload(festival.id, film.id),
            headers=headers,
        ).json()

        resp = client.patch(
            f"/api/awards/{award['id']}/recipient-verification",
            json={"notes": "sin campo verified"},
            headers=headers,
        )
        assert resp.status_code == 422
