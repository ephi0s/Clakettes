"""Tests for chat/message endpoints."""

import pytest
from starlette.websockets import WebSocketDisconnect

from app.auth import create_session, revoke_session


def _login(client, create_user, username, email):
    user, password = create_user(username=username, email=email)
    resp = client.post(
        "/api/users/login",
        json={
            "username": user.username,
            "password": password,
        },
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class TestListMessages:
    """Tests for GET /api/chat/messages."""

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/chat/messages", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_messages(self, client, auth_headers, create_user):
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        client.post(
            "/api/chat/messages",
            json={
                "content": "Hello!",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        client.post(
            "/api/chat/messages",
            json={
                "content": "How are you?",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        response = client.get("/api/chat/messages", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_filter_by_sender(self, client, auth_headers, create_user):
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        client.post(
            "/api/chat/messages",
            json={
                "content": "From sender",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        response = client.get(f"/api/chat/messages?sender_id={sender.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["content"] == "From sender"

    def test_list_dm_cross_access_forbidden(self, client, auth_headers, create_user):
        """A third user cannot read the DM thread between two other users."""
        headers_a, user_a = auth_headers
        user_b, _ = create_user(username="user_b", email="user_b@example.com")
        client.post(
            "/api/chat/messages",
            json={
                "content": "Private A-B",
                "sender_id": user_a.id,
                "receiver_id": user_b.id,
            },
            headers=headers_a,
        )
        user_c_headers = _login(client, create_user, "user_c", "user_c@example.com")
        response = client.get(
            f"/api/chat/messages?sender_id={user_a.id}&receiver_id={user_b.id}",
            headers=user_c_headers,
        )
        assert response.status_code == 403

    def test_list_dm_other_sender_hides_foreign_thread(self, client, auth_headers, create_user):
        """Filtering by another user's sender_id never leaks a DM the caller is not in."""
        headers_a, user_a = auth_headers
        user_b, _ = create_user(username="user_b", email="user_b@example.com")
        client.post(
            "/api/chat/messages",
            json={
                "content": "Private A-B",
                "sender_id": user_a.id,
                "receiver_id": user_b.id,
            },
            headers=headers_a,
        )
        user_c_headers = _login(client, create_user, "user_c", "user_c@example.com")
        response = client.get(f"/api/chat/messages?sender_id={user_a.id}", headers=user_c_headers)
        assert response.status_code == 200
        assert response.json()["items"] == []


class TestCreateMessage:
    """Tests for POST /api/chat/messages."""

    def _create_message(self, client, headers, **kwargs):
        data = {
            "content": kwargs.get("content", "Hello!"),
            "sender_id": kwargs.get("sender_id", 0),
            "receiver_id": kwargs.get("receiver_id"),
        }
        return client.post("/api/chat/messages", json=data, headers=headers)

    def test_create_success(self, client, auth_headers, create_user):
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        response = self._create_message(
            client, headers, receiver_id=receiver.id, content="Test message", sender_id=sender.id
        )  # noqa: E501
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Test message"
        assert data["sender_id"] == sender.id
        assert data["receiver_id"] == receiver.id
        assert data["is_read"] is False

    def test_create_requires_auth(self, client, create_user):
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        response = client.post(
            "/api/chat/messages",
            json={
                "content": "No auth",
                "sender_id": 0,
                "receiver_id": receiver.id,
            },
        )
        assert response.status_code == 401

    def test_create_sender_id_override(self, client, auth_headers, create_user):
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        response = client.post(
            "/api/chat/messages",
            json={
                "content": "Spoof attempt",
                "sender_id": 9999,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["sender_id"] == sender.id


class TestMarkRead:
    """Tests for PUT /api/chat/messages/{id}/read."""

    def test_mark_read_success(self, client, auth_headers, create_user):
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        create_resp = client.post(
            "/api/chat/messages",
            json={
                "content": "Read me",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        msg_id = create_resp.json()["id"]
        response = client.put(f"/api/chat/messages/{msg_id}/read", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Message marked as read"

    def test_mark_read_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put("/api/chat/messages/9999/read", headers=headers)
        assert response.status_code == 404

    def test_mark_read_cross_access_forbidden(self, client, auth_headers, create_user):
        """A non-participant cannot mark someone else's message as read."""
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        create_resp = client.post(
            "/api/chat/messages",
            json={
                "content": "Read me",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        msg_id = create_resp.json()["id"]
        intruder_headers = _login(client, create_user, "intruder", "intruder@example.com")
        response = client.put(f"/api/chat/messages/{msg_id}/read", headers=intruder_headers)
        assert response.status_code == 403


class TestDeleteMessage:
    """Tests for DELETE /api/chat/messages/{id}."""

    def test_delete_success(self, client, auth_headers, create_user):
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        create_resp = client.post(
            "/api/chat/messages",
            json={
                "content": "Delete me",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        msg_id = create_resp.json()["id"]
        response = client.delete(f"/api/chat/messages/{msg_id}", headers=headers)
        assert response.status_code == 200

    def test_delete_requires_auth(self, client, auth_headers, create_user):
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        create_resp = client.post(
            "/api/chat/messages",
            json={
                "content": "Test",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        msg_id = create_resp.json()["id"]
        response = client.delete(f"/api/chat/messages/{msg_id}")
        assert response.status_code == 401

    def test_delete_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/chat/messages/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_cross_access_forbidden(self, client, auth_headers, create_user):
        """A non-sender cannot delete someone else's message."""
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        create_resp = client.post(
            "/api/chat/messages",
            json={
                "content": "Delete me",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        msg_id = create_resp.json()["id"]
        intruder_headers = _login(client, create_user, "intruder", "intruder@example.com")
        response = client.delete(f"/api/chat/messages/{msg_id}", headers=intruder_headers)
        assert response.status_code == 403

    def test_delete_receiver_forbidden(self, client, auth_headers, create_user):
        """The receiver cannot delete the sender's message."""
        headers, sender = auth_headers
        receiver, _ = create_user(username="receiver", email="receiver@example.com")
        create_resp = client.post(
            "/api/chat/messages",
            json={
                "content": "Delete me",
                "sender_id": sender.id,
                "receiver_id": receiver.id,
            },
            headers=headers,
        )
        msg_id = create_resp.json()["id"]
        receiver_headers = _login(client, create_user, "receiver2", "receiver2@example.com")
        response = client.delete(f"/api/chat/messages/{msg_id}", headers=receiver_headers)
        assert response.status_code == 403


class TestWebSocketAuth:
    """WebSocket authentication validates the session, not just the JWT."""

    @staticmethod
    def _ws_url(token):
        return f"/api/chat/ws?token={token}"

    def test_ws_connect_valid_session(self, client, db_session, create_user):
        """A valid access token with an active session can connect."""
        user, _ = create_user()
        _, access_token, _ = create_session(db_session, user.id)
        with client.websocket_connect(self._ws_url(access_token)) as ws:
            ws.send_json({"type": "ping"})
            assert ws.receive_json() == {"type": "pong"}

    def test_ws_revoked_session_rejected(self, client, db_session, create_user):
        """A revoked session must not be able to connect to the WebSocket."""
        user, _ = create_user()
        session, access_token, _ = create_session(db_session, user.id)
        revoke_session(db_session, session)
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(self._ws_url(access_token)):
                pass
        assert exc_info.value.code == 4001

    def test_ws_refresh_type_token_rejected(self, client, db_session, create_user):
        """A refresh-type JWT must not be able to connect to the WebSocket."""
        from datetime import datetime, timedelta, timezone
        import jwt
        from app.auth import _hash_token
        from app.config import settings
        from app.models.user_session import UserSession

        user, _ = create_user()
        token = jwt.encode(
            {
                "sub": str(user.id),
                "user_id": user.id,
                "type": "refresh",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        db_session.add(
            UserSession(
                user_id=user.id,
                token_hash=_hash_token(token),
                refresh_token_hash="placeholder",
                is_active=True,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        )
        db_session.commit()
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(self._ws_url(token)):
                pass
        assert exc_info.value.code == 4001
