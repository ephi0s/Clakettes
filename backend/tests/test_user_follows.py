"""Tests for user follow endpoints."""


def _login(client, create_user, username, email):
    user, password = create_user(username=username, email=email)
    resp = client.post("/api/users/login", json={"username": user.username, "password": password})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}, user


def test_follow_requires_auth(client, create_user):
    u1, _ = create_user(username="faa1", email="f1@x.com")
    u2, _ = create_user(username="faa2", email="f2@x.com")
    r = client.post(f"/api/users/{u2.id}/follow")
    assert r.status_code == 401
    r = client.get(f"/api/users/{u2.id}/follow/status")
    assert r.status_code == 401


def test_follow_self_rejected(client, create_user):
    h, u = _login(client, create_user, "selfs1", "selfs1@x.com")
    r = client.post(f"/api/users/{u.id}/follow", headers=h)
    assert r.status_code == 400


def test_follow_status_lists_and_unfollow(client, create_user):
    h1, u1 = _login(client, create_user, "fol1", "fol1@x.com")
    h2, u2 = _login(client, create_user, "fol2", "fol2@x.com")

    r = client.get(f"/api/users/{u2.id}/follow/status", headers=h1)
    assert r.status_code == 200
    assert r.json()["is_following"] is False

    r = client.post(f"/api/users/{u2.id}/follow", headers=h1)
    assert r.status_code == 201
    assert r.json()["follower_id"] == u1.id
    assert r.json()["followed_id"] == u2.id

    r = client.post(f"/api/users/{u2.id}/follow", headers=h1)
    assert r.status_code == 201
    assert r.json()["id"] == 1

    r = client.get(f"/api/users/{u2.id}/follow/status", headers=h1)
    assert r.json() == {"is_following": True, "followers_count": 1, "following_count": 0}

    r = client.get(f"/api/users/{u2.id}/followers", headers=h1)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["follower_id"] == u1.id

    r = client.get(f"/api/users/{u1.id}/following", headers=h1)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["followed_id"] == u2.id

    r = client.get(f"/api/users/{u1.id}/follow/status", headers=h2)
    assert r.json()["followers_count"] == 0
    assert r.json()["following_count"] == 1

    r = client.delete(f"/api/users/{u2.id}/follow", headers=h1)
    assert r.status_code == 200
    r = client.get(f"/api/users/{u2.id}/follow/status", headers=h1)
    assert r.json()["is_following"] is False
    assert r.json()["followers_count"] == 0
