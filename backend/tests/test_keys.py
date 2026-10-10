"""Tests for E2EE public key endpoints."""

PUBLIC_KEY = "6iU5P3HlXm9qZ2TvW4rY7bNc8kF0sD1jA3gH5fJ6kL0"


class TestUploadPublicKey:
    """Tests for POST /api/users/me/public-key."""

    def test_upload_success(self, client, auth_headers):
        headers, user = auth_headers
        response = client.post(
            "/api/users/me/public-key",
            json={
                "public_key_x25519": PUBLIC_KEY,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["public_key_x25519"] == PUBLIC_KEY
        assert len(data["key_identifier"]) == 16

    def test_upload_requires_auth(self, client):
        response = client.post(
            "/api/users/me/public-key",
            json={
                "public_key_x25519": PUBLIC_KEY,
            },
        )
        assert response.status_code == 401

    def test_upload_rotation(self, client, auth_headers):
        headers, user = auth_headers
        client.post(
            "/api/users/me/public-key",
            json={
                "public_key_x25519": PUBLIC_KEY,
            },
            headers=headers,
        )
        new_key = "aB3xY7zK9pQ2wE5rT8uI1oP4sD6fG0hJ2kL4nM6bV8cC0"
        response = client.post(
            "/api/users/me/public-key",
            json={
                "public_key_x25519": new_key,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["public_key_x25519"] == new_key
        assert data["rotated_at"] is not None


class TestGetPublicKey:
    """Tests for GET /api/users/{user_id}/public-key."""

    def test_get_own_key(self, client, auth_headers):
        headers, user = auth_headers
        client.post(
            "/api/users/me/public-key",
            json={
                "public_key_x25519": PUBLIC_KEY,
            },
            headers=headers,
        )
        response = client.get(f"/api/users/{user.id}/public-key", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["public_key_x25519"] == PUBLIC_KEY

    def test_get_other_user_key(self, client, auth_headers, create_user, db_session):
        headers, _ = auth_headers
        other_user, _ = create_user(username="other", email="other@example.com")
        from app.auth import create_session

        _, token, _ = create_session(db_session, other_user.id)
        other_headers = {"Authorization": f"Bearer {token}"}
        client.post(
            "/api/users/me/public-key",
            json={
                "public_key_x25519": PUBLIC_KEY,
            },
            headers=other_headers,
        )
        response = client.get(f"/api/users/{other_user.id}/public-key", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == other_user.id
        assert data["public_key_x25519"] == PUBLIC_KEY

    def test_get_not_found(self, client, auth_headers, create_user):
        headers, _ = auth_headers
        other_user, _ = create_user(username="nokey", email="nokey@example.com")
        response = client.get(f"/api/users/{other_user.id}/public-key", headers=headers)
        assert response.status_code == 404
        assert "no public key" in response.json()["detail"].lower()

    def test_get_requires_auth(self, client, auth_headers):
        headers, user = auth_headers
        client.post(
            "/api/users/me/public-key",
            json={
                "public_key_x25519": PUBLIC_KEY,
            },
            headers=headers,
        )
        response = client.get(f"/api/users/{user.id}/public-key")
        assert response.status_code == 401
