"""Tests for authentication endpoints."""

from datetime import datetime, timedelta, timezone

import jwt

from app.auth import _hash_token
from app.config import settings
from app.models.user_session import UserSession


class TestLogin:
    """Tests for POST /api/users/login."""

    def test_login_success(self, client, create_user):
        user, password = create_user()
        response = client.post(
            "/api/users/login",
            json={
                "username": user.username,
                "password": password,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == user.username

    def test_login_wrong_password(self, client, create_user):
        user, password = create_user()
        response = client.post(
            "/api/users/login",
            json={
                "username": user.username,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/users/login",
            json={
                "username": "nobody",
                "password": "nope",
            },
        )
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Tests that write endpoints require auth."""

    def test_create_festival_requires_auth(self, client):
        response = client.post("/api/festivals/", json={"name": "Test"})
        assert response.status_code == 401

    def test_create_shortfilm_requires_auth(self, client):
        response = client.post("/api/shortfilms/", json={"title": "Test"})
        assert response.status_code == 401

    def test_create_message_requires_auth(self, client):
        response = client.post(
            "/api/chat/messages",
            json={
                "sender_id": 1,
                "receiver_id": 2,
                "content": "hi",
            },
        )
        assert response.status_code == 401

    def test_update_user_requires_auth(self, client):
        response = client.put("/api/users/1", json={"full_name": "Hacked"})
        assert response.status_code == 401

    def test_get_festivals_public(self, client):
        response = client.get("/api/festivals/")
        assert response.status_code == 200


class TestTokenTypeValidation:
    """A JWT whose type is not 'access' must never grant access."""

    @staticmethod
    def _forge_token(user_id, token_type):
        from app.auth import JWT_ALGORITHM

        payload = {
            "sub": str(user_id),
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
        }
        if token_type is not None:
            payload["type"] = token_type
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)

    def _register_session_for_token(self, db_session, user_id, token):
        db_session.add(
            UserSession(
                user_id=user_id,
                token_hash=_hash_token(token),
                refresh_token_hash="placeholder",
                is_active=True,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        )
        db_session.commit()

    def test_refresh_type_token_rejected(self, client, create_user, db_session):
        """A token signed as type=refresh must not work as an access token."""
        user, _ = create_user()
        token = self._forge_token(user.id, "refresh")
        self._register_session_for_token(db_session, user.id, token)
        response = client.get("/api/chat/messages", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401

    def test_missing_type_token_rejected(self, client, create_user, db_session):
        """A signed token without a type claim must not work as an access token."""
        user, _ = create_user()
        token = self._forge_token(user.id, None)
        self._register_session_for_token(db_session, user.id, token)
        response = client.get("/api/chat/messages", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401

    def test_access_token_still_accepted(self, client, create_user, db_session):
        """Genuine access tokens keep working."""
        from app.auth import create_session

        user, _ = create_user()
        _, access_token, _ = create_session(db_session, user.id)
        response = client.get("/api/chat/messages", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
