"""Integration tests for FormDefinition API endpoints."""

from datetime import datetime, timedelta, timezone

from app.models.form_definition import (
    FormLink,
    SubmissionStatus,
)
from app.models.festival import Festival

# =============================================================================
# Form Definition CRUD
# =============================================================================


class TestCreateForm:
    """POST /api/forms/"""

    def test_create_user_creation_form(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/forms/",
            json={"title": "User Creation", "form_type": "user_creation"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "User Creation"
        assert data["form_type"] == "user_creation"
        assert data["is_active"] is True
        assert data["require_auth"] is True
        assert data["id"] is not None

    def test_create_festival_registration_form(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        fest = Festival(name="Fest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.post(
            "/api/forms/",
            json={
                "title": "Fest Reg",
                "form_type": "festival_registration",
                "festival_id": fest.id,
                "description": "Register for the festival",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Fest Reg"
        assert data["form_type"] == "festival_registration"
        assert data["festival_id"] == fest.id
        assert data["description"] == "Register for the festival"

    def test_create_internal_form(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/forms/",
            json={
                "title": "Internal",
                "form_type": "internal",
                "is_public": False,
                "max_submissions": 100,
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Internal"
        assert data["form_type"] == "internal"
        assert data["max_submissions"] == 100
        assert data["is_public"] is False

    def test_create_with_pages(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/forms/",
            json={
                "title": "Multi-page Form",
                "form_type": "user_creation",
                "pages": [
                    {"title": "Page 1", "sort_order": 0, "description": "First page"},
                    {"title": "Page 2", "sort_order": 1},
                ],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["pages"]) == 2
        assert data["pages"][0]["title"] == "Page 1"
        assert data["pages"][1]["title"] == "Page 2"

    def test_create_requires_auth(self, client):
        response = client.post(
            "/api/forms/",
            json={"title": "No Auth", "form_type": "user_creation"},
        )
        assert response.status_code == 401


class TestListForms:
    """GET /api/forms/"""

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/forms/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 20
        assert data["pages"] == 1

    def test_list_requires_auth(self, client):
        response = client.get("/api/forms/")
        assert response.status_code == 401

    def test_list_with_forms(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        client.post("/api/forms/", json={"title": "Form A", "form_type": "user_creation"}, headers=headers)
        client.post("/api/forms/", json={"title": "Form B", "form_type": "internal"}, headers=headers)
        client.post("/api/forms/", json={"title": "Form C", "form_type": "festival_registration"}, headers=headers)
        response = client.get("/api/forms/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_pagination(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        for i in range(5):
            client.post("/api/forms/", json={"title": f"Form {i}", "form_type": "user_creation"}, headers=headers)
        response = client.get("/api/forms/?page=1&size=2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["pages"] == 3
        assert len(data["items"]) == 2


class TestGetForm:
    """GET /api/forms/{form_id}"""

    def test_get_success(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Get Me", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.get(f"/api/forms/{form_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Get Me"

    def test_get_requires_auth(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Auth Get", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.get(f"/api/forms/{form_id}")
        assert response.status_code == 401

    def test_get_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/forms/99999", headers=headers)
        assert response.status_code == 404

    def test_get_with_pages_and_fields(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={
                "title": "Deep Form",
                "form_type": "user_creation",
                "pages": [
                    {
                        "title": "Page 1",
                        "sort_order": 0,
                        "fields": [
                            {
                                "field_type": "string",
                                "label": "Name",
                                "is_required": True,
                                "sort_order": 0,
                            }
                        ],
                    }
                ],
            },
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.get(f"/api/forms/{form_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["pages"]) == 1
        assert data["pages"][0]["title"] == "Page 1"
        assert len(data["pages"][0]["fields"]) == 1
        assert data["pages"][0]["fields"][0]["label"] == "Name"
        assert data["pages"][0]["fields"][0]["field_type"] == "string"


class TestUpdateForm:
    """PUT /api/forms/{form_id}"""

    def test_update_title_and_description(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Original", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.put(
            f"/api/forms/{form_id}",
            json={"title": "Updated Title", "description": "Updated description"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"

    def test_update_form_type(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Switch", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.put(
            f"/api/forms/{form_id}",
            json={"form_type": "internal"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["form_type"] == "internal"

    def test_update_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put(
            "/api/forms/99999",
            json={"title": "Nope"},
            headers=headers,
        )
        assert response.status_code == 404

    def test_update_requires_auth(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Auth Test", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.put(
            f"/api/forms/{form_id}",
            json={"title": "Hacked"},
        )
        assert response.status_code == 401


class TestDeleteForm:
    """DELETE /api/forms/{form_id}"""

    def test_delete_success(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Delete Me", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        delete_resp = client.delete(f"/api/forms/{form_id}", headers=headers)
        assert delete_resp.status_code == 200
        get_resp = client.get(f"/api/forms/{form_id}", headers=headers)
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/forms/99999", headers=headers)
        assert response.status_code == 404

    def test_delete_requires_auth(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Auth Delete", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.delete(f"/api/forms/{form_id}")
        assert response.status_code == 401


# =============================================================================
# Form Pages
# =============================================================================


class TestCrudPages:
    """CRUD for form pages."""

    def test_create_page(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Page Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "New Page", "description": "A brand new page", "sort_order": 0},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Page"
        assert data["description"] == "A brand new page"
        assert data["form_id"] == form_id

    def test_create_page_with_fields(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Form With Fields", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/pages/",
            json={
                "title": "Page With Fields",
                "sort_order": 0,
                "fields": [
                    {"field_type": "string", "label": "Name", "is_required": True, "sort_order": 0},
                    {"field_type": "email", "label": "Email", "sort_order": 1},
                ],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["fields"]) == 2

    def test_update_page(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Update Page Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Original Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        response = client.put(
            f"/api/forms/{form_id}/pages/{page_id}",
            json={"title": "Updated Page", "description": "Changed"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Page"
        assert data["description"] == "Changed"

    def test_delete_page(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Delete Page Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Delete Me", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        delete_resp = client.delete(f"/api/forms/{form_id}/pages/{page_id}", headers=headers)
        assert delete_resp.status_code == 200
        form_resp = client.get(f"/api/forms/{form_id}", headers=headers)
        assert len(form_resp.json()["pages"]) == 0

    def test_page_not_found_in_form(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Form A", "form_type": "user_creation"},
            headers=headers,
        )
        form_id_a = create_resp.json()["id"]
        create_resp_b = client.post(
            "/api/forms/",
            json={"title": "Form B", "form_type": "user_creation"},
            headers=headers,
        )
        form_id_b = create_resp_b.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id_a}/pages/",
            json={"title": "Page of A", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        response = client.put(
            f"/api/forms/{form_id_b}/pages/{page_id}",
            json={"title": "Hacked"},
            headers=headers,
        )
        assert response.status_code == 404


# =============================================================================
# Form Fields
# =============================================================================


class TestCrudFields:
    """CRUD for form fields."""

    def test_create_field_of_each_type(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Fields Galore", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Fields Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        for field_type in ["string", "email", "number", "boolean", "url", "date"]:
            response = client.post(
                f"/api/forms/{form_id}/pages/{page_id}/fields/",
                json={"field_type": field_type, "label": f"Field {field_type}", "sort_order": 0},
                headers=headers,
            )
            assert response.status_code == 201, f"Failed for type {field_type}"
            assert response.json()["field_type"] == field_type

    def test_update_field(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Update Field Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        field_resp = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={"field_type": "string", "label": "Old Label", "sort_order": 0},
            headers=headers,
        )
        field_id = field_resp.json()["id"]
        response = client.put(
            f"/api/forms/{form_id}/fields/{field_id}",
            json={"label": "New Label", "is_required": True, "placeholder": "Enter value"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "New Label"
        assert data["is_required"] is True
        assert data["placeholder"] == "Enter value"

    def test_delete_field(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Delete Field Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        field_resp = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={"field_type": "string", "label": "Delete Me", "sort_order": 0},
            headers=headers,
        )
        field_id = field_resp.json()["id"]
        delete_resp = client.delete(f"/api/forms/{form_id}/fields/{field_id}", headers=headers)
        assert delete_resp.status_code == 200
        form_resp = client.get(f"/api/forms/{form_id}", headers=headers)
        pages = form_resp.json()["pages"]
        assert len(pages) == 1
        assert len(pages[0]["fields"]) == 0

    def test_field_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Field Not Found", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.put(
            f"/api/forms/{form_id}/fields/99999",
            json={"label": "Ghost"},
            headers=headers,
        )
        assert response.status_code == 404


class TestFieldOptions:
    """Fields with select/multiselect options."""

    def test_create_select_with_options(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Select Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={
                "field_type": "select",
                "label": "Favorite Color",
                "is_required": True,
                "sort_order": 0,
                "options": [
                    {"value": "red", "label": "Red", "sort_order": 0},
                    {"value": "blue", "label": "Blue", "sort_order": 1},
                    {"value": "green", "label": "Green", "sort_order": 2},
                ],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["field_type"] == "select"
        assert len(data["options"]) == 3
        assert data["options"][0]["value"] == "red"
        assert data["options"][0]["label"] == "Red"

    def test_create_multiselect_with_options(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Multi Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={
                "field_type": "multiselect",
                "label": "Skills",
                "sort_order": 0,
                "options": [
                    {"value": "python", "label": "Python"},
                    {"value": "flutter", "label": "Flutter"},
                ],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["field_type"] == "multiselect"
        assert len(data["options"]) == 2


# =============================================================================
# Conditional Fields
# =============================================================================


class TestFormWithConditionalFields:
    """Fields with dependsOnFieldId."""

    def test_conditional_field(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Conditional Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]

        field_one = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={"field_type": "boolean", "label": "Has Experience", "sort_order": 0},
            headers=headers,
        )
        field_one_id = field_one.json()["id"]

        field_two = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={
                "field_type": "string",
                "label": "Years of Experience",
                "sort_order": 1,
                "depends_on_field_id": field_one_id,
                "depends_on_value": "true",
            },
            headers=headers,
        )
        assert field_two.status_code == 201
        data = field_two.json()
        assert data["depends_on_field_id"] == field_one_id
        assert data["depends_on_value"] == "true"
        assert data["label"] == "Years of Experience"


# =============================================================================
# Form Responses
# =============================================================================


class TestSubmitResponse:
    """POST /api/forms/public/{token}/submit"""

    def test_submit_response(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={
                "title": "Submit Form",
                "form_type": "user_creation",
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        field_resp = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={"field_type": "string", "label": "Name", "sort_order": 0, "is_required": True},
            headers=headers,
        )
        field_id = field_resp.json()["id"]

        link_resp = client.post(
            f"/api/forms/{form_id}/links/",
            json={},
            headers=headers,
        )
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {str(field_id): "John Doe"}},
            headers=headers,
        )
        assert submit_resp.status_code == 200
        data = submit_resp.json()
        assert data["form_id"] == form_id
        assert data["status"] == SubmissionStatus.SUBMITTED.value
        assert data["submitted_at"] is not None
        assert len(data["field_responses"]) == 1
        assert data["field_responses"][0]["value"] == "John Doe"

    def test_submit_response_empty_values(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={
                "title": "Empty Submit",
                "form_type": "user_creation",
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={"field_type": "string", "label": "Name", "sort_order": 0},
            headers=headers,
        )
        link_resp = client.post(
            f"/api/forms/{form_id}/links/",
            json={},
            headers=headers,
        )
        token = link_resp.json()["token"]
        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        assert submit_resp.status_code == 200
        assert submit_resp.json()["form_id"] == form_id


class TestListResponses:
    """GET /api/forms/{form_id}/responses/"""

    def test_list_responses_empty(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "List Empty", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.get(f"/api/forms/{form_id}/responses/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_responses_with_data(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={
                "title": "List Data",
                "form_type": "user_creation",
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )

        response = client.get(f"/api/forms/{form_id}/responses/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_responses_form_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/forms/99999/responses/", headers=headers)
        assert response.status_code == 404


class TestResponseReview:
    """POST /api/forms/responses/{response_id}/approve and /reject"""

    def test_approve_response(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={
                "title": "Approve Test",
                "form_type": "user_creation",
                "requires_approval": True,
            },
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        response_id = submit_resp.json()["id"]
        assert submit_resp.json()["status"] == SubmissionStatus.DRAFT.value

        approve_resp = client.post(
            f"/api/forms/responses/{response_id}/approve",
            headers=headers,
        )
        assert approve_resp.status_code == 200
        assert approve_resp.json()["status"] == SubmissionStatus.APPROVED.value
        assert approve_resp.json()["reviewer_id"] is not None

    def test_reject_response(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={
                "title": "Reject Test",
                "form_type": "user_creation",
                "requires_approval": True,
            },
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        response_id = submit_resp.json()["id"]

        reject_resp = client.post(
            f"/api/forms/responses/{response_id}/reject?reason=Not+eligible",
            headers=headers,
        )
        assert reject_resp.status_code == 200
        data = reject_resp.json()
        assert data["status"] == SubmissionStatus.REJECTED.value
        assert "Not eligible" in data["review_notes"]

    def test_approve_already_approved(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={
                "title": "Double Approve",
                "form_type": "user_creation",
                "requires_approval": True,
            },
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        response_id = submit_resp.json()["id"]

        client.post(f"/api/forms/responses/{response_id}/approve", headers=headers)
        second = client.post(f"/api/forms/responses/{response_id}/approve", headers=headers)
        assert second.status_code == 400


# =============================================================================
# Form Links
# =============================================================================


class TestCreateLink:
    """POST /api/forms/{form_id}/links/"""

    def test_create_default_link(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Link Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/links/",
            json={},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["token"] is not None
        assert len(data["token"]) > 0
        assert data["is_active"] is True
        assert data["is_public"] is True
        assert data["is_unique"] is False
        assert data["use_count"] == 0

    def test_create_unique_link(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Unique Link Form", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/links/",
            json={"is_unique": True, "notes": "One-time use link"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_unique"] is True
        assert data["notes"] == "One-time use link"

    def test_create_link_form_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post("/api/forms/99999/links/", json={}, headers=headers)
        assert response.status_code == 404


class TestListLinks:
    """GET /api/forms/{form_id}/links/"""

    def test_list_links_empty(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "No Links", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        response = client.get(f"/api/forms/{form_id}/links/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_links_with_data(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post(
            "/api/forms/",
            json={"title": "Many Links", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = create_resp.json()["id"]
        client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        client.post(f"/api/forms/{form_id}/links/", json={"is_unique": True}, headers=headers)

        response = client.get(f"/api/forms/{form_id}/links/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2


# =============================================================================
# Public Form Access (no auth required for GET)
# =============================================================================


class TestPublicFormAccess:
    """GET /api/forms/public/{token}"""

    def test_get_public_form(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Public Form",
                "form_type": "user_creation",
                "is_public": True,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        public_resp = client.get(f"/api/forms/public/{token}")
        assert public_resp.status_code == 200
        data = public_resp.json()
        assert data["title"] == "Public Form"
        assert data["id"] == form_id
        assert "is_active" not in data

    def test_get_public_form_not_found(self, client):
        response = client.get("/api/forms/public/invalidtoken123")
        assert response.status_code == 404

    def test_get_public_form_inactive_link(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Inactive Public",
                "form_type": "user_creation",
                "is_public": True,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link = FormLink(form_id=form_id, token="deadlink", is_active=False)
        db_session.add(link)
        db_session.commit()

        response = client.get("/api/forms/public/deadlink")
        assert response.status_code == 404

    def test_get_public_form_expired(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Expired Public",
                "form_type": "user_creation",
                "is_public": True,
                "ends_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link = FormLink(form_id=form_id, token="expiredlink", is_active=True)
        db_session.add(link)
        db_session.commit()

        response = client.get("/api/forms/public/expiredlink")
        assert response.status_code == 404


class TestPublicFormSubmit:
    """POST /api/forms/public/{token}/submit"""

    def test_submit_via_public_endpoint(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Public Submit",
                "form_type": "user_creation",
                "is_public": True,
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        assert submit_resp.status_code == 200
        data = submit_resp.json()
        assert data["status"] == SubmissionStatus.SUBMITTED.value
        assert data["link_token"] == token

    def test_submit_invalid_token(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/forms/public/badtoken/submit",
            json={"field_values": {}},
            headers=headers,
        )
        assert response.status_code == 404


class TestPublicFormSubmitAuth:
    """POST /api/forms/public/{token}/submit with optional auth."""

    def test_submit_anonymous_public_form(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Anonymous Public",
                "form_type": "user_creation",
                "is_public": True,
                "require_auth": False,
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
        )
        assert submit_resp.status_code == 200
        data = submit_resp.json()
        assert data["user_id"] is None

    def test_submit_with_token_associates_user(self, client, auth_headers):
        headers, user = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Auth Public",
                "form_type": "user_creation",
                "is_public": True,
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        assert submit_resp.status_code == 200
        assert submit_resp.json()["user_id"] == user.id

    def test_submit_anonymous_requires_auth_form(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Auth Required",
                "form_type": "user_creation",
                "is_public": True,
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
        )
        assert submit_resp.status_code == 401


class TestPublicFormSubmitLimit:
    """max_submissions enforcement."""

    def test_submit_limit_reached(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Limited Form",
                "form_type": "user_creation",
                "is_public": True,
                "requires_approval": False,
                "max_submissions": 1,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        first = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        assert first.status_code == 200

        second = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        assert second.status_code == 400
        assert "full" in second.json()["detail"].lower()


# =============================================================================
# Auth Requirements
# =============================================================================


class TestAuthRequired:
    """Verify non-public endpoints reject unauthenticated requests."""

    def test_create_form_no_auth(self, client):
        response = client.post(
            "/api/forms/",
            json={"title": "No Auth", "form_type": "user_creation"},
        )
        assert response.status_code == 401

    def test_create_page_no_auth(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={"title": "No Auth Page", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
        )
        assert response.status_code == 401

    def test_create_field_no_auth(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={"title": "No Auth Field", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        response = client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={"field_type": "string", "label": "X", "sort_order": 0},
        )
        assert response.status_code == 401

    def test_delete_form_no_auth(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={"title": "No Auth Delete", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        response = client.delete(f"/api/forms/{form_id}")
        assert response.status_code == 401

    def test_list_links_no_auth(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={"title": "No Auth Links", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        response = client.get(f"/api/forms/{form_id}/links/")
        assert response.status_code == 401

    def test_list_responses_no_auth(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={"title": "No Auth Responses", "form_type": "user_creation"},
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        response = client.get(f"/api/forms/{form_id}/responses/")
        assert response.status_code == 401


# =============================================================================
# Response Validation (required field enforcement)
# =============================================================================


class TestResponseValidation:
    """Submit with required fields — API does not enforce validation at service level."""

    def test_submit_missing_required_field(self, client, auth_headers):
        headers, _ = auth_headers
        form_resp = client.post(
            "/api/forms/",
            json={
                "title": "Validation Form",
                "form_type": "user_creation",
                "requires_approval": False,
            },
            headers=headers,
        )
        form_id = form_resp.json()["id"]
        page_resp = client.post(
            f"/api/forms/{form_id}/pages/",
            json={"title": "Page", "sort_order": 0},
            headers=headers,
        )
        page_id = page_resp.json()["id"]
        client.post(
            f"/api/forms/{form_id}/pages/{page_id}/fields/",
            json={
                "field_type": "string",
                "label": "Required Field",
                "is_required": True,
                "sort_order": 0,
            },
            headers=headers,
        )

        link_resp = client.post(f"/api/forms/{form_id}/links/", json={}, headers=headers)
        token = link_resp.json()["token"]

        submit_resp = client.post(
            f"/api/forms/public/{token}/submit",
            json={"field_values": {}},
            headers=headers,
        )
        assert submit_resp.status_code == 200
        assert submit_resp.json()["status"] == SubmissionStatus.SUBMITTED.value
