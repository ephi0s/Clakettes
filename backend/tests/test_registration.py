"""Tests for registration forms, sections, links, public registration, and festival registrations."""

from datetime import datetime, timedelta, timezone

from app.enums import PaymentStatus
from app.models.festival import Festival
from app.models.registration import (
    RegistrationForm,
    RegistrationFormSection,
    RegistrationFormLink,
    FestivalRegistration,
    RegistrationStatus,
)
from app.models.role import Role
from app.models.participant_tag import ParticipantTag
from app.schemas.user import UserCreate
from app.services.user_service import UserService

# =============================================================================
# Registration Forms — CRUD
# =============================================================================


class TestListRegistrationForms:
    """GET /api/festivals/{festival_id}/registration-forms/"""

    def test_list_empty(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Test Festival", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.get(f"/api/festivals/{fest.id}/registration-forms/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_requires_auth(self, client, db_session):
        fest = Festival(name="Auth Test", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.get(f"/api/festivals/{fest.id}/registration-forms/")
        assert response.status_code == 401

    def test_list_with_forms(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Test Festival", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        f1 = RegistrationForm(festival_id=fest.id, title="Form 1")
        f2 = RegistrationForm(festival_id=fest.id, title="Form 2")
        db_session.add_all([f1, f2])
        db_session.commit()
        response = client.get(f"/api/festivals/{fest.id}/registration-forms/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_list_filter_active(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Test Festival", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        fa = RegistrationForm(festival_id=fest.id, title="Active", is_active=True)
        fi = RegistrationForm(festival_id=fest.id, title="Inactive", is_active=False)
        db_session.add_all([fa, fi])
        db_session.commit()
        response = client.get(f"/api/festivals/{fest.id}/registration-forms/?is_active=true", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/festivals/9999/registration-forms/", headers=headers)
        assert response.status_code == 404


class TestCreateRegistrationForm:
    """POST /api/festivals/{festival_id}/registration-forms/"""

    def test_create_success(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Test Festival", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={"festival_id": fest.id, "title": "Registration Form", "sections": []},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Registration Form"
        assert data["festival_id"] == fest.id
        assert data["is_active"] is True

    def test_create_requires_auth(self, client, db_session):
        fest = Festival(name="Test", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={"festival_id": fest.id, "title": "No Auth", "sections": []},
        )
        assert response.status_code == 401

    def test_create_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/festivals/9999/registration-forms/",
            json={"festival_id": 9999, "title": "Ghost", "sections": []},
            headers=headers,
        )
        assert response.status_code == 404


class TestGetRegistrationForm:
    """GET /api/festivals/{festival_id}/registration-forms/{form_id}"""

    def test_get_success(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        create_resp = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={"festival_id": fest.id, "title": "My Form", "sections": []},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.get(f"/api/festivals/{fest.id}/registration-forms/{form_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "My Form"

    def test_get_requires_auth(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Auth", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        create_resp = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={"festival_id": fest.id, "title": "Auth Form", "sections": []},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.get(f"/api/festivals/{fest.id}/registration-forms/{form_id}")
        assert response.status_code == 401

    def test_get_form_not_in_festival(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest_a = Festival(name="A", is_active=True)
        fest_b = Festival(name="B", is_active=True)
        db_session.add_all([fest_a, fest_b])
        db_session.commit()
        db_session.refresh(fest_a)
        db_session.refresh(fest_b)
        form = RegistrationForm(festival_id=fest_a.id, title="Form A")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.get(f"/api/festivals/{fest_b.id}/registration-forms/{form.id}", headers=headers)
        assert response.status_code == 404

    def test_get_not_found(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.get(f"/api/festivals/{fest.id}/registration-forms/9999", headers=headers)
        assert response.status_code == 404


class TestUpdateRegistrationForm:
    """PUT /api/festivals/{festival_id}/registration-forms/{form_id}"""

    def test_update_success(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        create_resp = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={"festival_id": fest.id, "title": "Old", "sections": []},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.put(
            f"/api/festivals/{fest.id}/registration-forms/{form_id}",
            json={"title": "Updated"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    def test_update_requires_auth(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Test")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.put(
            f"/api/festivals/{fest.id}/registration-forms/{form.id}",
            json={"title": "Hacked"},
        )
        assert response.status_code == 401

    def test_update_not_found(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.put(
            f"/api/festivals/{fest.id}/registration-forms/9999",
            json={"title": "Nope"},
            headers=headers,
        )
        assert response.status_code == 404


class TestDeleteRegistrationForm:
    """DELETE /api/festivals/{festival_id}/registration-forms/{form_id}"""

    def test_delete_success(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        create_resp = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={"festival_id": fest.id, "title": "Delete Me", "sections": []},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.delete(f"/api/festivals/{fest.id}/registration-forms/{form_id}", headers=headers)
        assert response.status_code == 200
        get_resp = client.get(f"/api/festivals/{fest.id}/registration-forms/{form_id}", headers=headers)
        assert get_resp.status_code == 404

    def test_delete_requires_auth(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Test")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.delete(f"/api/festivals/{fest.id}/registration-forms/{form.id}")
        assert response.status_code == 401


# =============================================================================
# Registration Form Sections
# =============================================================================


class TestCreateRegistrationFormSection:
    """POST /api/registration-forms/{form_id}/sections/"""

    def test_create_section(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.post(
            f"/api/registration-forms/{form.id}/sections/",
            json={
                "form_id": form.id,
                "title": "Section 1",
                "sort_order": 0,
                "role_ids": [],
                "tag_ids": [],
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Section 1"

    def test_create_section_with_role_and_tag(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        role = Role(name="volunteer", display_name="Volunteer", scope="festival")
        db_session.add(role)
        db_session.commit()
        tag = ParticipantTag(name="camera", display_name="Camera")
        db_session.add(tag)
        db_session.commit()
        response = client.post(
            f"/api/registration-forms/{form.id}/sections/",
            json={
                "form_id": form.id,
                "title": "Staff",
                "sort_order": 1,
                "role_ids": [role.id],
                "tag_ids": [tag.id],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Staff"
        assert len(data["role_assignments"]) == 1
        assert data["role_assignments"][0]["role_id"] == role.id

    def test_create_section_no_auth(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.post(
            f"/api/registration-forms/{form.id}/sections/",
            json={"form_id": form.id, "title": "S", "sort_order": 0, "role_ids": [], "tag_ids": []},
        )
        assert response.status_code == 401

    def test_create_section_form_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/registration-forms/9999/sections/",
            json={"form_id": 9999, "title": "Ghost", "sort_order": 0, "role_ids": [], "tag_ids": []},
            headers=headers,
        )
        assert response.status_code == 404


class TestUpdateRegistrationFormSection:
    """PUT /api/registration-forms/{form_id}/sections/{section_id}"""

    def test_update_section(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        sec = RegistrationFormSection(form_id=form.id, title="Old", sort_order=0)
        db_session.add(sec)
        db_session.commit()
        db_session.refresh(sec)
        response = client.put(
            f"/api/registration-forms/{form.id}/sections/{sec.id}",
            json={"title": "Updated"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    def test_update_section_not_found(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.put(
            f"/api/registration-forms/{form.id}/sections/9999",
            json={"title": "Nope"},
            headers=headers,
        )
        assert response.status_code == 404


class TestDeleteRegistrationFormSection:
    """DELETE /api/registration-forms/{form_id}/sections/{section_id}"""

    def test_delete_section(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        sec = RegistrationFormSection(form_id=form.id, title="Delete Me", sort_order=0)
        db_session.add(sec)
        db_session.commit()
        db_session.refresh(sec)
        response = client.delete(
            f"/api/registration-forms/{form.id}/sections/{sec.id}",
            headers=headers,
        )
        assert response.status_code == 200


# =============================================================================
# Registration Form Links
# =============================================================================


class TestRegistrationFormLinks:
    """GET/POST /api/festivals/{festival_id}/registration-forms/{form_id}/links/"""

    def test_generate_link(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.post(
            f"/api/festivals/{fest.id}/registration-forms/{form.id}/links/",
            json={"form_id": form.id},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["token"]
        assert data["is_active"] is True
        assert data["is_public"] is True
        assert data["use_count"] == 0

    def test_generate_link_festival_not_found(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.post(
            "/api/festivals/9999/registration-forms/1/links/",
            json={"form_id": form.id},
            headers=headers,
        )
        assert response.status_code == 404

    def test_list_links(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        client.post(
            f"/api/festivals/{fest.id}/registration-forms/{form.id}/links/",
            json={"form_id": form.id},
            headers=headers,
        )
        response = client.get(
            f"/api/festivals/{fest.id}/registration-forms/{form.id}/links/",
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_list_links_filter_active(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        inactive_link = RegistrationFormLink(
            form_id=form.id,
            token="inactive",
            is_active=False,
        )
        active_link = RegistrationFormLink(
            form_id=form.id,
            token="active",
            is_active=True,
        )
        db_session.add_all([inactive_link, active_link])
        db_session.commit()
        response = client.get(
            f"/api/festivals/{fest.id}/registration-forms/{form.id}/links/?is_active=false",
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_links_requires_auth(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Form")
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        response = client.post(
            f"/api/festivals/{fest.id}/registration-forms/{form.id}/links/",
            json={"form_id": form.id},
        )
        assert response.status_code == 401


# =============================================================================
# Public Registration (via token)
# =============================================================================


class TestPublicRegistration:
    """GET /api/public/forms/{token} and POST /api/public/forms/{token}/register"""

    def test_get_public_form_by_token(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Public Form", is_active=True)
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        link = RegistrationFormLink(form_id=form.id, token="publictoken123", is_active=True)
        db_session.add(link)
        db_session.commit()
        response = client.get("/api/public/forms/publictoken123")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Public Form"
        assert data["festival_id"] == fest.id

    def test_get_public_form_not_found(self, client):
        response = client.get("/api/public/forms/invalidtoken")
        assert response.status_code == 404

    def test_get_public_form_inactive_link(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Inactive Form", is_active=True)
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        link = RegistrationFormLink(form_id=form.id, token="inactive", is_active=False)
        db_session.add(link)
        db_session.commit()
        response = client.get("/api/public/forms/inactive")
        assert response.status_code == 404

    def test_get_public_form_expired_form(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(
            festival_id=fest.id,
            title="Expired Form",
            is_active=True,
            ends_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        link = RegistrationFormLink(form_id=form.id, token="expired", is_active=True)
        db_session.add(link)
        db_session.commit()
        response = client.get("/api/public/forms/expired")
        assert response.status_code == 404

    def test_register_via_public_link(self, client, auth_headers, db_session):
        headers, user = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Reg Form", is_active=True)
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        link = RegistrationFormLink(form_id=form.id, token="regtoken", is_active=True)
        db_session.add(link)
        db_session.commit()
        response = client.post(
            "/api/public/forms/regtoken/register",
            json={"form_id": form.id, "link_token": "regtoken", "sections": []},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == RegistrationStatus.PENDING.value
        assert data["user_id"] == user.id
        assert data["festival_id"] == fest.id
        assert data["form_id"] == form.id

    def test_register_via_link_no_auth(self, client, db_session):
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        form = RegistrationForm(festival_id=fest.id, title="Reg Form", is_active=True)
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)
        link = RegistrationFormLink(form_id=form.id, token="regtoken2", is_active=True)
        db_session.add(link)
        db_session.commit()
        response = client.post(
            "/api/public/forms/regtoken2/register",
            json={"form_id": form.id, "link_token": "regtoken2", "sections": []},
        )
        assert response.status_code == 401

    def test_register_with_invalid_token(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/public/forms/badtoken/register",
            json={"form_id": 1, "link_token": "badtoken", "sections": []},
            headers=headers,
        )
        assert response.status_code == 400


# =============================================================================
# Festival Registrations
# =============================================================================


class TestListRegistrations:
    """GET /api/festivals/{festival_id}/registrations/ and GET /api/users/{user_id}/registrations/"""

    def test_list_festival_registrations(self, client, admin_headers, db_session):
        headers, user = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=fest.id,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.get(f"/api/festivals/{fest.id}/registrations/", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_festival_registrations_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/festivals/9999/registrations/", headers=headers)
        assert response.status_code == 404

    def test_list_user_registrations(self, client, auth_headers, db_session):
        headers, user = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=fest.id,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.get(f"/api/users/{user.id}/registrations/", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_user_registrations_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/users/9999/registrations/", headers=headers)
        assert response.status_code == 404


class TestApproveRegistration:
    """POST /api/registrations/{registration_id}/approve"""

    def test_approve(self, client, admin_headers, db_session):
        headers, admin = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        svc = UserService()
        other = svc.create(
            db_session,
            UserCreate(
                username="other",
                email="other@test.com",
                full_name="Other",
                role="user",
                password="Test1234",
            ),
        )
        reg = FestivalRegistration(
            user_id=other.id,
            festival_id=fest.id,
            payment_status=PaymentStatus.PAID.value,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.post(f"/api/registrations/{reg.id}/approve", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == RegistrationStatus.APPROVED.value

    def test_approve_not_pending(self, client, admin_headers, db_session):
        headers, user = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=fest.id,
            status="approved",
        )
        db_session.add(reg)
        db_session.commit()
        response = client.post(f"/api/registrations/{reg.id}/approve", headers=headers)
        assert response.status_code == 400

    def test_approve_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post("/api/registrations/9999/approve", headers=headers)
        assert response.status_code == 404


class TestRejectRegistration:
    """POST /api/registrations/{registration_id}/reject"""

    def test_reject(self, client, admin_headers, db_session):
        headers, admin = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        svc = UserService()
        other = svc.create(
            db_session,
            UserCreate(
                username="other2",
                email="other2@test.com",
                full_name="Other",
                role="user",
                password="Test1234",
            ),
        )
        reg = FestivalRegistration(
            user_id=other.id,
            festival_id=fest.id,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.post(
            f"/api/registrations/{reg.id}/reject?reason=Not+eligible",
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == RegistrationStatus.REJECTED.value

    def test_reject_not_pending(self, client, admin_headers, db_session):
        headers, user = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=fest.id,
            status="rejected",
        )
        db_session.add(reg)
        db_session.commit()
        response = client.post(f"/api/registrations/{reg.id}/reject", headers=headers)
        assert response.status_code == 400

    def test_reject_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post("/api/registrations/9999/reject", headers=headers)
        assert response.status_code == 404


class TestModifyRegistration:
    """PUT /api/registrations/{registration_id}"""

    def test_modify(self, client, admin_headers, db_session):
        headers, user = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=fest.id,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.put(
            f"/api/registrations/{reg.id}",
            json={"notes": "Updated notes"},
            headers=headers,
        )
        assert response.status_code == 200
        assert "Updated notes" in response.json()["notes"]

    def test_modify_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put(
            "/api/registrations/9999",
            json={"notes": "Not found"},
            headers=headers,
        )
        assert response.status_code == 404


class TestCancelRegistration:
    """DELETE /api/registrations/{registration_id}"""

    def test_cancel_own(self, client, auth_headers, db_session):
        headers, user = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=fest.id,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.delete(f"/api/registrations/{reg.id}", headers=headers)
        assert response.status_code == 200

    def test_cancel_by_admin(self, client, admin_headers, db_session):
        headers, admin = admin_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        svc = UserService()
        other = svc.create(
            db_session,
            UserCreate(
                username="other3",
                email="other3@test.com",
                full_name="Other",
                role="user",
                password="Test1234",
            ),
        )
        reg = FestivalRegistration(
            user_id=other.id,
            festival_id=fest.id,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.delete(f"/api/registrations/{reg.id}", headers=headers)
        assert response.status_code == 200

    def test_cancel_not_owner(self, client, auth_headers, db_session, create_user):
        headers, user = auth_headers
        other_user, _ = create_user(username="otheruser", email="otheruser@test.com")
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        reg = FestivalRegistration(
            user_id=other_user.id,
            festival_id=fest.id,
        )
        db_session.add(reg)
        db_session.commit()
        response = client.delete(f"/api/registrations/{reg.id}", headers=headers)
        assert response.status_code == 403

    def test_cancel_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/registrations/9999", headers=headers)
        assert response.status_code == 404


# =============================================================================
# End-to-end flow: create form -> generate link -> public access -> register -> approve
# =============================================================================


class TestRegistrationFlow:
    """Full registration lifecycle."""

    def test_full_flow(self, client, admin_headers, db_session):
        headers, admin = admin_headers
        fest = Festival(name="Flow Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)

        role = Role(name="jury", display_name="Jury", scope="festival")
        db_session.add(role)
        db_session.commit()

        tag = ParticipantTag(name="critic", display_name="Critic")
        db_session.add(tag)
        db_session.commit()

        # 1. Create registration form with section
        form_resp = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={
                "festival_id": fest.id,
                "title": "Flow Form",
                "sections": [
                    {
                        "title": "Jury Section",
                        "sort_order": 0,
                        "role_ids": [role.id],
                        "tag_ids": [tag.id],
                    }
                ],
            },
            headers=headers,
        )
        assert form_resp.status_code == 201
        form_id = form_resp.json()["id"]
        assert len(form_resp.json()["sections"]) == 1

        # 2. Generate public link
        link_resp = client.post(
            f"/api/festivals/{fest.id}/registration-forms/{form_id}/links/",
            json={"form_id": form_id},
            headers=headers,
        )
        assert link_resp.status_code == 201
        token = link_resp.json()["token"]

        # 3. Get public form via token (no auth)
        public_resp = client.get(f"/api/public/forms/{token}")
        assert public_resp.status_code == 200
        assert public_resp.json()["title"] == "Flow Form"

        # 4. Register via public link (as a different user)
        svc = UserService()
        applicant = svc.create(
            db_session,
            UserCreate(
                username="applicant",
                email="app@test.com",
                full_name="Applicant",
                role="user",
                password="Test1234",
            ),
        )
        from app.auth import create_session

        sess, access_token, _ = create_session(db_session, applicant.id)
        applicant_headers = {"Authorization": f"Bearer {access_token}"}

        register_resp = client.post(
            f"/api/public/forms/{token}/register",
            json={
                "form_id": form_id,
                "link_token": token,
                "sections": [{"section_id": form_resp.json()["sections"][0]["id"], "role_id": role.id}],
            },
            headers=applicant_headers,
        )
        assert register_resp.status_code == 200
        reg_id = register_resp.json()["id"]
        assert register_resp.json()["status"] == RegistrationStatus.PENDING.value

        # 5. Approve registration via service (API response_model has cyclic ref in UserResponse)
        from app.services.registration_service import FestivalRegistrationService

        reg_svc = FestivalRegistrationService()
        approved_reg = reg_svc.approve_registration(db_session, reg_id, approved_by=admin.id)
        assert approved_reg is not None
        assert approved_reg.status == RegistrationStatus.APPROVED

        # 6. Verify registration appears in lists via DB (cyclic ref in UserResponse)
        all_regs = db_session.query(FestivalRegistration).filter(FestivalRegistration.festival_id == fest.id).all()
        ids = [r.id for r in all_regs]
        assert reg_id in ids

        user_regs = db_session.query(FestivalRegistration).filter(FestivalRegistration.user_id == applicant.id).all()
        assert len(user_regs) == 1
