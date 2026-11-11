"""Tests for participant-initiated verification requests on participant tags."""

from datetime import datetime, timezone


def _create_festival(db_session, name="Verification Request Festival"):
    from app.models.festival import Festival

    festival = Festival(name=name, is_active=True)
    db_session.add(festival)
    db_session.commit()
    db_session.refresh(festival)
    return festival


def _create_tag(db_session, name="student", display_name="Estudiante"):
    from app.models.participant_tag import ParticipantTag

    tag = ParticipantTag(name=name, display_name=display_name, category="other")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


def _assign_tag(client, headers, user_id, tag_id, festival_id):
    resp = client.post(
        f"/api/users/{user_id}/participant-tags/",
        json={"user_id": user_id, "tag_id": tag_id, "festival_id": festival_id},
        headers=headers,
    )
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


class TestParticipantVerificationRequest:
    def test_request_with_document(self, client, db_session, admin_headers, auth_headers):
        headers, _ = admin_headers
        user_headers, participant = auth_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        assigned = _assign_tag(client, headers, participant.id, tag.id, festival.id)

        resp = client.post(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/request-verification",
            json={
                "method": "document",
                "document_url": "/uploads/documents/matricula.pdf",
                "notes": "Matrícula del curso 2026/2027",
            },
            headers=user_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["verification_status"] == "pending"
        assert data["verification_method"] == "document"
        assert data["verification_document_url"] == "/uploads/documents/matricula.pdf"
        assert data["verification_requested_at"] is not None
        assert data["verified_at"] is None

    def test_self_declared_request_needs_no_document(self, client, db_session, admin_headers, auth_headers):
        headers, _ = admin_headers
        user_headers, participant = auth_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session, name="resident", display_name="Residente")
        assigned = _assign_tag(client, headers, participant.id, tag.id, festival.id)

        resp = client.post(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/request-verification",
            json={"method": "self_declared", "notes": "Resido en el municipio"},
            headers=user_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["verification_status"] == "pending"
        assert resp.json()["verification_document_url"] is None

    def test_document_method_requires_url(self, client, db_session, admin_headers, auth_headers):
        headers, _ = admin_headers
        user_headers, participant = auth_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        assigned = _assign_tag(client, headers, participant.id, tag.id, festival.id)

        resp = client.post(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/request-verification",
            json={"method": "document"},
            headers=user_headers,
        )
        assert resp.status_code == 400

        invalid = client.post(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/request-verification",
            json={"method": "invented"},
            headers=user_headers,
        )
        assert invalid.status_code == 422

    def test_only_owner_can_request(self, client, db_session, admin_headers, auth_headers, create_user):
        headers, _ = admin_headers
        user_headers, _ = auth_headers
        other, _ = create_user(username="other_participant", email="other_participant@example.com")
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        assigned = _assign_tag(client, headers, other.id, tag.id, festival.id)

        forbidden = client.post(
            f"/api/users/{other.id}/participant-tags/{assigned['id']}/request-verification",
            json={"method": "document", "document_url": "/uploads/documents/x.pdf"},
            headers=user_headers,
        )
        assert forbidden.status_code == 403

        anonymous = client.post(
            f"/api/users/{other.id}/participant-tags/{assigned['id']}/request-verification",
            json={"method": "document", "document_url": "/uploads/documents/x.pdf"},
        )
        assert anonymous.status_code == 401

        missing = client.post(
            f"/api/users/{other.id}/participant-tags/9999/request-verification",
            json={"method": "document", "document_url": "/uploads/documents/x.pdf"},
            headers=headers,
        )
        assert missing.status_code == 404

    def test_cannot_request_when_already_verified(self, client, db_session, admin_headers, auth_headers):
        headers, _ = admin_headers
        user_headers, participant = auth_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        assigned = _assign_tag(client, headers, participant.id, tag.id, festival.id)
        client.patch(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified", "method": "external"},
            headers=headers,
        )

        resp = client.post(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/request-verification",
            json={"method": "document", "document_url": "/uploads/documents/x.pdf"},
            headers=user_headers,
        )
        assert resp.status_code == 400

    def test_organizer_sees_pending_request_and_verifies(self, client, db_session, admin_headers, auth_headers):
        headers, _ = admin_headers
        user_headers, participant = auth_headers
        festival = _create_festival(db_session)
        tag = _create_tag(db_session)
        assigned = _assign_tag(client, headers, participant.id, tag.id, festival.id)
        client.post(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/request-verification",
            json={"method": "document", "document_url": "/uploads/documents/matricula.pdf"},
            headers=user_headers,
        )

        organizer_headers, organizer = auth_headers
        _make_organizer(db_session, organizer.id, festival.id)
        pending = client.get(
            f"/api/users/{participant.id}/participant-tags/?festival_id={festival.id}&verification_status=pending",
            headers=organizer_headers,
        )
        assert pending.status_code == 200
        assert pending.json()["total"] == 1

        verified = client.patch(
            f"/api/users/{participant.id}/participant-tags/{assigned['id']}/verify",
            json={"status": "verified", "method": "document", "notes": "Documento correcto"},
            headers=organizer_headers,
        )
        assert verified.status_code == 200
        data = verified.json()
        assert data["verification_status"] == "verified"
        assert data["verification_document_url"] == "/uploads/documents/matricula.pdf"
        assert data["verified_by"] == organizer.id


class TestDocumentUpload:
    def test_upload_pdf_document(self, client, auth_headers, tmp_path, monkeypatch):
        from pypdf import PdfWriter

        monkeypatch.chdir(tmp_path)
        headers, _ = auth_headers
        pdf = tmp_path / "certificado.pdf"
        writer = PdfWriter()
        writer.add_blank_page(100, 100)
        with open(pdf, "wb") as f:
            writer.write(f)
        with open(pdf, "rb") as f:
            resp = client.post(
                "/api/uploads/document",
                files={"file": ("certificado.pdf", f, "application/pdf")},
                headers=headers,
            )
        assert resp.status_code == 200
        assert resp.json()["url"].startswith("/uploads/documents/")

    def test_rejects_non_pdf_document(self, client, auth_headers, tmp_path):
        headers, _ = auth_headers
        resp = client.post(
            "/api/uploads/document",
            files={"file": ("foto.png", b"not a pdf", "image/png")},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_requires_authentication(self, client):
        resp = client.post(
            "/api/uploads/document",
            files={"file": ("certificado.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 401
