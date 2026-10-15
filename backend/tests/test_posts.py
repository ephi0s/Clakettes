"""Tests for profile wall publications (microblogging) endpoints."""


def _login(client, create_user, username, email):
    user, password = create_user(username=username, email=email)
    resp = client.post(
        "/api/users/login",
        json={"username": user.username, "password": password},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}, user


def _make_festival(client, headers, name="Fest"):
    resp = client.post("/api/festivals/", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


class TestUserWall:
    def test_create_and_list(self, client, auth_headers):
        headers, user = auth_headers
        resp = client.post(
            f"/api/users/{user.id}/posts/",
            json={"content": "Hello **world**"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["content"] == "Hello **world**"
        assert resp.json()["target_user_id"] == user.id

        listed = client.get(f"/api/users/{user.id}/posts/")
        assert listed.status_code == 200
        assert listed.json()["total"] == 1

    def test_create_requires_auth(self, client, create_user):
        user, _ = create_user(username="wall", email="wall@example.com")
        resp = client.post(f"/api/users/{user.id}/posts/", json={"content": "Hi"})
        assert resp.status_code in (401, 403)

    def test_create_unknown_user_404(self, client, auth_headers):
        headers, _ = auth_headers
        resp = client.post("/api/users/999999/posts/", json={"content": "Hi"}, headers=headers)
        assert resp.status_code == 404

    def test_embed_type_validated(self, client, auth_headers):
        headers, user = auth_headers
        resp = client.post(
            f"/api/users/{user.id}/posts/",
            json={"content": "x", "embed_url": "https://example.com/v", "embed_type": "nope"},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_embed_post_roundtrip(self, client, auth_headers):
        headers, user = auth_headers
        resp = client.post(
            f"/api/users/{user.id}/posts/",
            json={
                "content": "Watch this",
                "embed_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "embed_type": "youtube",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["embed_type"] == "youtube"


class TestFestivalWall:
    def test_create_and_list(self, client, auth_headers):
        headers, _ = auth_headers
        fest = _make_festival(client, headers)
        resp = client.post(
            f"/api/festivals/{fest['id']}/posts/",
            json={"content": "Welcome to the festival"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["festival_id"] == fest["id"]

        listed = client.get(f"/api/festivals/{fest['id']}/posts/")
        assert listed.status_code == 200
        assert listed.json()["total"] == 1


class TestReplies:
    def test_reply_flow(self, client, auth_headers):
        headers, user = auth_headers
        post = client.post(f"/api/users/{user.id}/posts/", json={"content": "Parent"}, headers=headers).json()
        reply = client.post(f"/api/posts/{post['id']}/replies/", json={"content": "Child"}, headers=headers)
        assert reply.status_code == 201
        assert reply.json()["parent_post_id"] == post["id"]

        listed = client.get(f"/api/posts/{post['id']}/replies/")
        assert listed.json()["total"] == 1
        single = client.get(f"/api/posts/{post['id']}")
        assert single.json()["reply_count"] == 1

    def test_reply_to_reply_rejected(self, client, auth_headers):
        headers, user = auth_headers
        post = client.post(f"/api/users/{user.id}/posts/", json={"content": "P"}, headers=headers).json()
        reply = client.post(f"/api/posts/{post['id']}/replies/", json={"content": "R"}, headers=headers).json()
        resp = client.post(f"/api/posts/{reply['id']}/replies/", json={"content": "R2"}, headers=headers)
        assert resp.status_code == 400

    def test_locked_post_blocks_strangers(self, client, auth_headers, create_user):
        headers, user = auth_headers
        post = client.post(
            f"/api/users/{user.id}/posts/",
            json={"content": "Locked", "allow_replies": False},
            headers=headers,
        ).json()
        other_headers, _ = _login(client, create_user, "other", "other@example.com")
        resp = client.post(f"/api/posts/{post['id']}/replies/", json={"content": "Nope"}, headers=other_headers)
        assert resp.status_code == 403


class TestEditDelete:
    def test_author_can_edit(self, client, auth_headers):
        headers, user = auth_headers
        post = client.post(f"/api/users/{user.id}/posts/", json={"content": "v1"}, headers=headers).json()
        resp = client.put(f"/api/posts/{post['id']}", json={"content": "v2"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["content"] == "v2"

    def test_stranger_cannot_edit(self, client, auth_headers, create_user):
        headers, user = auth_headers
        post = client.post(f"/api/users/{user.id}/posts/", json={"content": "mine"}, headers=headers).json()
        other_headers, _ = _login(client, create_user, "stranger", "stranger@example.com")
        resp = client.put(f"/api/posts/{post['id']}", json={"content": "hacked"}, headers=other_headers)
        assert resp.status_code == 403

    def test_author_can_delete(self, client, auth_headers):
        headers, user = auth_headers
        post = client.post(f"/api/users/{user.id}/posts/", json={"content": "bye"}, headers=headers).json()
        resp = client.delete(f"/api/posts/{post['id']}", headers=headers)
        assert resp.status_code == 200


class TestModeration:
    def test_organizer_can_pin_and_hide(self, client, auth_headers):
        headers, _ = auth_headers
        fest = _make_festival(client, headers)
        post = client.post(f"/api/festivals/{fest['id']}/posts/", json={"content": "Mod me"}, headers=headers).json()
        resp = client.post(
            f"/api/posts/{post['id']}/moderate",
            json={"is_pinned": True, "is_hidden": True},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_pinned"] is True
        assert resp.json()["is_hidden"] is True

        public = client.get(f"/api/festivals/{fest['id']}/posts/")
        assert public.json()["total"] == 0

    def test_stranger_cannot_moderate(self, client, auth_headers, create_user):
        headers, _ = auth_headers
        fest = _make_festival(client, headers)
        post = client.post(f"/api/festivals/{fest['id']}/posts/", json={"content": "Keep"}, headers=headers).json()
        other_headers, _ = _login(client, create_user, "outsider", "outsider@example.com")
        resp = client.post(f"/api/posts/{post['id']}/moderate", json={"is_hidden": True}, headers=other_headers)
        assert resp.status_code == 403

    def test_wall_owner_can_moderate_own_wall(self, client, auth_headers, create_user):
        headers, owner = auth_headers
        post = client.post(f"/api/users/{owner.id}/posts/", json={"content": "Owner post"}, headers=headers).json()
        other_headers, _ = _login(client, create_user, "writer", "writer@example.com")
        client.post(f"/api/users/{owner.id}/posts/", json={"content": "Guest post"}, headers=other_headers)
        resp = client.post(f"/api/posts/{post['id']}/moderate", json={"is_pinned": True}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["is_pinned"] is True
