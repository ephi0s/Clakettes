"""Tests for short film CRUD endpoints."""


class TestListShortFilms:
    """Tests for GET /api/shortfilms/."""

    def test_list_empty(self, client):
        response = client.get("/api/shortfilms/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_shortfilms(self, client, auth_headers):
        headers, user = auth_headers
        client.post("/api/shortfilms/", json={"title": "Film 1", "user_id": user.id}, headers=headers)
        client.post("/api/shortfilms/", json={"title": "Film 2", "user_id": user.id}, headers=headers)
        response = client.get("/api/shortfilms/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_filter_by_festival(self, client, auth_headers):
        headers, user = auth_headers
        client.post(
            "/api/shortfilms/", json={"title": "Fest Film", "festival_id": 1, "user_id": user.id}, headers=headers
        )  # noqa: E501
        client.post("/api/shortfilms/", json={"title": "No Fest Film", "user_id": user.id}, headers=headers)
        response = client.get("/api/shortfilms/?festival_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Fest Film"

    def test_list_filter_by_is_public(self, client, auth_headers):
        headers, user = auth_headers
        client.post(
            "/api/shortfilms/", json={"title": "Public", "is_public": True, "user_id": user.id}, headers=headers
        )  # noqa: E501
        client.post(
            "/api/shortfilms/", json={"title": "Private", "is_public": False, "user_id": user.id}, headers=headers
        )  # noqa: E501
        response = client.get("/api/shortfilms/?is_public=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Public"


class TestCreateShortFilm:
    """Tests for POST /api/shortfilms/."""

    def _create_shortfilm(self, client, headers, **kwargs):
        data = {
            "title": kwargs.get("title", "Test Film"),
            "description": kwargs.get("description", "A test short film"),
            "duration": kwargs.get("duration", 120),
            "is_public": kwargs.get("is_public", True),
            "user_id": kwargs.get("user_id"),
        }
        return client.post("/api/shortfilms/", json=data, headers=headers)

    def test_create_success(self, client, auth_headers):
        headers, user = auth_headers
        response = self._create_shortfilm(client, headers, user_id=user.id)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Film"
        assert data["duration"] == 120
        assert data["is_public"] is True

    def test_create_requires_auth(self, client):
        response = client.post("/api/shortfilms/", json={"title": "No Auth", "user_id": 1})
        assert response.status_code == 401

    def test_create_requires_title(self, client, auth_headers):
        headers, user = auth_headers
        response = client.post("/api/shortfilms/", json={"user_id": user.id}, headers=headers)
        assert response.status_code == 422


class TestGetShortFilm:
    """Tests for GET /api/shortfilms/{id}."""

    def test_get_success(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Test", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        response = client.get(f"/api/shortfilms/{film_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test"

    def test_get_not_found(self, client):
        response = client.get("/api/shortfilms/9999")
        assert response.status_code == 404


class TestUpdateShortFilm:
    """Tests for PUT /api/shortfilms/{id}."""

    def test_update_owner(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Old", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        response = client.put(f"/api/shortfilms/{film_id}", json={"title": "New"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "New"

    def test_update_other_user_forbidden(self, client, create_user, auth_headers, db_session):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Mine", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        other_user, _ = create_user(username="other", email="other@example.com")
        from app.auth import create_session

        session, token, _ = create_session(db_session, other_user.id)
        other_headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/api/shortfilms/{film_id}", json={"title": "Hacked"}, headers=other_headers)
        assert response.status_code == 403

    def test_admin_can_update_any(self, client, auth_headers, admin_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "User Film", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        admin_hdrs, _ = admin_headers
        response = client.put(f"/api/shortfilms/{film_id}", json={"title": "Admin Edit"}, headers=admin_hdrs)
        assert response.status_code == 200
        assert response.json()["title"] == "Admin Edit"

    def test_update_requires_auth(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Fest", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        response = client.put(f"/api/shortfilms/{film_id}", json={"title": "Hacked"})
        assert response.status_code == 401

    def test_update_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put("/api/shortfilms/9999", json={"title": "Nope"}, headers=headers)
        assert response.status_code == 404


class TestDeleteShortFilm:
    """Tests for DELETE /api/shortfilms/{id}."""

    def test_delete_owner(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Doomed", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        response = client.delete(f"/api/shortfilms/{film_id}", headers=headers)
        assert response.status_code == 200

    def test_delete_other_user_forbidden(self, client, create_user, auth_headers, db_session):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Mine", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        other_user, _ = create_user(username="other", email="other@example.com")
        from app.auth import create_session

        session, token, _ = create_session(db_session, other_user.id)
        other_headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/api/shortfilms/{film_id}", headers=other_headers)
        assert response.status_code == 403

    def test_admin_can_delete_any(self, client, auth_headers, admin_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "User Film", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        admin_hdrs, _ = admin_headers
        response = client.delete(f"/api/shortfilms/{film_id}", headers=admin_hdrs)
        assert response.status_code == 200

    def test_delete_requires_auth(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Fest", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        response = client.delete(f"/api/shortfilms/{film_id}")
        assert response.status_code == 401

    def test_delete_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/shortfilms/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_verify_gone(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/shortfilms/", json={"title": "Goner", "user_id": user.id}, headers=headers)
        film_id = create_resp.json()["id"]
        client.delete(f"/api/shortfilms/{film_id}", headers=headers)
        get_resp = client.get(f"/api/shortfilms/{film_id}")
        assert get_resp.status_code == 404
