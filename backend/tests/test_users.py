"""Tests for user CRUD endpoints."""


class TestCreateUser:
    """Tests for POST /api/users/."""

    def test_create_user_success(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/users/",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "full_name": "New User",
                "role": "user",
                "password": "Strong123",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

    def test_create_user_duplicate_username(self, client, admin_headers, create_user):
        headers, _ = admin_headers
        user, _ = create_user(username="dup")
        response = client.post(
            "/api/users/",
            json={
                "username": "dup",
                "email": "other@example.com",
                "password": "Strong123",
            },
            headers=headers,
        )
        assert response.status_code == 400

    def test_create_user_duplicate_email(self, client, admin_headers, create_user):
        headers, _ = admin_headers
        user, _ = create_user(email="taken@example.com")
        response = client.post(
            "/api/users/",
            json={
                "username": "other",
                "email": "taken@example.com",
                "password": "Strong123",
            },
            headers=headers,
        )
        assert response.status_code == 400


class TestGetUser:
    """Tests for GET /api/users/{id}."""

    def test_get_user_requires_auth(self, client, create_user):
        user, _ = create_user()
        response = client.get(f"/api/users/{user.id}")
        assert response.status_code == 401

    def test_get_user_success(self, client, create_user, db_session):
        user, _ = create_user()
        from app.auth import create_session

        session_obj, access_token, _ = create_session(db_session, user.id)
        response = client.get(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        assert response.json()["username"] == user.username
        assert response.json()["email"] == user.email

    def test_get_other_user_hides_email(self, client, create_user, db_session):
        user1, _ = create_user(username="user1", email="u1@example.com")
        user2, _ = create_user(username="user2", email="secret@example.com")
        from app.auth import create_session

        session_obj, access_token, _ = create_session(db_session, user1.id)
        response = client.get(f"/api/users/{user2.id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        assert response.json()["username"] == user2.username
        assert "email" not in response.json() or response.json()["email"] is None

    def test_admin_can_see_any_user_email(self, client, admin_headers, create_user):
        admin_token_headers, _ = admin_headers
        user, _ = create_user(username="target", email="target@example.com")
        response = client.get(f"/api/users/{user.id}", headers=admin_token_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "target@example.com"

    def test_get_user_not_found(self, client, admin_headers):
        admin_token_headers, _ = admin_headers
        response = client.get("/api/users/9999", headers=admin_token_headers)
        assert response.status_code == 404


class TestListUsers:
    """Tests for GET /api/users/."""

    def test_list_users_requires_auth(self, client):
        response = client.get("/api/users/")
        assert response.status_code == 401

    def test_list_users_hides_email_for_regular_users(self, client, create_user, db_session):
        other, _ = create_user(username="other", email="other@example.com")
        from app.auth import create_session

        session_obj, access_token, _ = create_session(db_session, other.id)
        response = client.get("/api/users/", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert "email" not in item or item["email"] is None

    def test_admin_list_users_includes_email(self, client, admin_headers, create_user):
        admin_token_headers, _ = admin_headers
        create_user(username="target", email="target@example.com")
        response = client.get("/api/users/", headers=admin_token_headers)
        assert response.status_code == 200
        emails = [u["email"] for u in response.json()["items"] if u["username"] == "target"]
        assert emails == ["target@example.com"]


class TestUpdateUser:
    """Tests for PUT /api/users/{id}."""

    def test_update_own_user(self, client, create_user, db_session):
        user, _ = create_user()
        from app.auth import create_session

        session_obj, access_token, _ = create_session(db_session, user.id)
        response = client.put(
            f"/api/users/{user.id}",
            json={
                "full_name": "Updated Name",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    def test_update_other_user_forbidden(self, client, create_user, db_session):
        user1, _ = create_user(username="user1", email="u1@example.com")
        user2, _ = create_user(username="user2", email="u2@example.com")
        from app.auth import create_session

        session_obj, access_token, _ = create_session(db_session, user1.id)
        response = client.put(
            f"/api/users/{user2.id}",
            json={
                "full_name": "Hacked",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 403

    def test_admin_can_update_any_user(self, client, admin_headers, create_user):
        admin_token_headers, _ = admin_headers
        user, _ = create_user(username="target", email="target@example.com")
        response = client.put(
            f"/api/users/{user.id}",
            json={
                "full_name": "Admin Updated",
            },
            headers=admin_token_headers,
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Admin Updated"


class TestDeleteUser:
    """Tests for DELETE /api/users/{id}."""

    def test_delete_user_requires_admin(self, client, create_user, db_session):
        user, _ = create_user()
        from app.auth import create_session

        session_obj, access_token, _ = create_session(db_session, user.id)
        response = client.delete(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 403

    def test_admin_can_delete_user(self, client, admin_headers, create_user):
        admin_token_headers, _ = admin_headers
        user, _ = create_user(username="target", email="target@example.com")
        response = client.delete(f"/api/users/{user.id}", headers=admin_token_headers)
        assert response.status_code == 200

    def test_delete_nonexistent_user(self, client, admin_headers):
        admin_token_headers, _ = admin_headers
        response = client.delete("/api/users/9999", headers=admin_token_headers)
        assert response.status_code == 404
