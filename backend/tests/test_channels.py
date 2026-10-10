"""Tests for channel CRUD and membership endpoints."""


class TestCreateChannel:
    """Tests for POST /api/channels."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "community"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def test_create_success(self, client, auth_headers):
        headers, _ = auth_headers
        response = self._create_channel(client, headers, name="Film Room")
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Film Room"
        assert data["channel_type"] == "community"
        assert data["is_active"] is True

    def test_create_requires_auth(self, client):
        response = client.post("/api/channels", json={"name": "No Auth"})
        assert response.status_code == 401


class TestListMyChannels:
    """Tests for GET /api/channels."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "community"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/channels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_channels(self, client, auth_headers):
        headers, _ = auth_headers
        self._create_channel(client, headers, name="Channel A")
        self._create_channel(client, headers, name="Channel B")
        response = client.get("/api/channels", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2


class TestListPublicChannels:
    """Tests for GET /api/channels/public."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "community"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def test_list_public(self, client, auth_headers):
        headers, _ = auth_headers
        self._create_channel(client, headers, name="Public Room")
        response = client.get("/api/channels/public", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["name"] == "Public Room"


class TestGetChannel:
    """Tests for GET /api/channels/{id}."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "community"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def test_get_success(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = self._create_channel(client, headers, name="My Channel")
        channel_id = create_resp.json()["id"]
        response = client.get(f"/api/channels/{channel_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "My Channel"

    def test_get_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/channels/9999", headers=headers)
        assert response.status_code == 404


class TestUpdateChannel:
    """Tests for PUT /api/channels/{id}."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "community"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def test_update_success(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = self._create_channel(client, headers, name="Old Name")
        channel_id = create_resp.json()["id"]
        response = client.put(f"/api/channels/{channel_id}", json={"name": "New Name"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    def test_update_requires_auth(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = self._create_channel(client, headers, name="Channel")
        channel_id = create_resp.json()["id"]
        response = client.put(f"/api/channels/{channel_id}", json={"name": "Hacked"})
        assert response.status_code == 401


class TestDeleteChannel:
    """Tests for DELETE /api/channels/{id}."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "community"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def test_delete_success(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = self._create_channel(client, headers, name="Doomed")
        channel_id = create_resp.json()["id"]
        response = client.delete(f"/api/channels/{channel_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Channel deactivated"
        # Verify it's marked inactive (soft delete)
        get_resp = client.get(f"/api/channels/{channel_id}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["is_active"] is False

    def test_delete_requires_auth(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = self._create_channel(client, headers, name="Channel")
        channel_id = create_resp.json()["id"]
        response = client.delete(f"/api/channels/{channel_id}")
        assert response.status_code == 401

    def test_delete_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/channels/9999", headers=headers)
        assert response.status_code == 404


class TestChannelMembers:
    """Tests for channel membership endpoints."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "community"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def test_add_member(self, client, auth_headers, create_user):
        headers, user = auth_headers
        other_user, _ = create_user(username="other", email="other@example.com")
        create_resp = self._create_channel(client, headers)
        channel_id = create_resp.json()["id"]
        response = client.post(
            f"/api/channels/{channel_id}/members",
            json={"user_id": other_user.id, "role": "member"},
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["user_id"] == other_user.id

    def test_list_members(self, client, auth_headers, create_user):
        headers, user = auth_headers
        other_user, _ = create_user(username="other", email="other@example.com")
        create_resp = self._create_channel(client, headers)
        channel_id = create_resp.json()["id"]
        client.post(
            f"/api/channels/{channel_id}/members",
            json={"user_id": other_user.id, "role": "member"},
            headers=headers,
        )
        response = client.get(f"/api/channels/{channel_id}/members", headers=headers)
        assert response.status_code == 200
        data = response.json()
        user_ids = [m["user_id"] for m in data]
        assert user.id in user_ids
        assert other_user.id in user_ids


class TestChannelAuthorization:
    """403/422 authorization tests (pilot for security block)."""

    def _create_channel(self, client, headers, **kwargs):
        data = {
            "name": kwargs.get("name", "Test Channel"),
            "description": kwargs.get("description", "A test channel"),
            "channel_type": kwargs.get("channel_type", "private"),
        }
        return client.post("/api/channels", json=data, headers=headers)

    def _outsider_headers(self, create_user, db_session):
        from app.auth import create_session

        outsider, _ = create_user(username="outsider", email="outsider@example.com")
        _, token, _ = create_session(db_session, outsider.id)
        return {"Authorization": f"Bearer {token}"}, outsider

    def test_private_detail_forbidden_for_outsider(self, client, auth_headers, create_user, db_session):
        headers, _ = auth_headers
        channel_id = self._create_channel(client, headers).json()["id"]
        outsider_headers, _ = self._outsider_headers(create_user, db_session)
        response = client.get(f"/api/channels/{channel_id}", headers=outsider_headers)
        assert response.status_code == 403

    def test_members_forbidden_for_outsider(self, client, auth_headers, create_user, db_session):
        headers, _ = auth_headers
        channel_id = self._create_channel(client, headers).json()["id"]
        outsider_headers, _ = self._outsider_headers(create_user, db_session)
        response = client.get(f"/api/channels/{channel_id}/members", headers=outsider_headers)
        assert response.status_code == 403

    def test_update_forbidden_for_plain_member(self, client, auth_headers, create_user, db_session):
        from app.auth import create_session

        headers, _ = auth_headers
        member, _ = create_user(username="member", email="member@example.com")
        channel_id = self._create_channel(client, headers).json()["id"]
        client.post(
            f"/api/channels/{channel_id}/members",
            json={"user_id": member.id, "role": "member"},
            headers=headers,
        )
        _, token, _ = create_session(db_session, member.id)
        member_headers = {"Authorization": f"Bearer {token}"}
        assert client.put(f"/api/channels/{channel_id}", json={"name": "X"}, headers=member_headers).status_code == 403
        assert client.delete(f"/api/channels/{channel_id}", headers=member_headers).status_code == 403
        assert (
            client.post(
                f"/api/channels/{channel_id}/members",
                json={"user_id": member.id, "role": "member"},
                headers=member_headers,
            ).status_code
            == 403
        )

    def test_invalid_role_rejected(self, client, auth_headers, create_user):
        headers, _ = auth_headers
        other_user, _ = create_user(username="other", email="other@example.com")
        channel_id = self._create_channel(client, headers).json()["id"]
        response = client.post(
            f"/api/channels/{channel_id}/members",
            json={"user_id": other_user.id, "role": "superadmin"},
            headers=headers,
        )
        assert response.status_code == 422
        client.post(
            f"/api/channels/{channel_id}/members",
            json={"user_id": other_user.id, "role": "member"},
            headers=headers,
        )
        response = client.put(
            f"/api/channels/{channel_id}/members/{other_user.id}/role",
            json={"role": "superadmin"},
            headers=headers,
        )
        assert response.status_code == 422
