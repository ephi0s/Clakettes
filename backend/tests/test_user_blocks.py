"""Tests for user blocking endpoints."""


def _login(client, create_user, username, email):
    user, password = create_user(username=username, email=email)
    resp = client.post("/api/users/login", json={"username": user.username, "password": password})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}, user


def test_block_requires_auth(client, create_user):
    u1, _ = create_user(username="aaa1", email="a1@x.com")
    u2, _ = create_user(username="aaa2", email="a2@x.com")
    r = client.post(f"/api/users/{u1.id}/blocks/", json={"blocked_id": u2.id})
    assert r.status_code == 401


def test_block_self_rejected(client, create_user):
    h, u = _login(client, create_user, "self1", "self1@x.com")
    r = client.post(f"/api/users/{u.id}/blocks/", json={"blocked_id": u.id}, headers=h)
    assert r.status_code == 400


def test_block_and_list_and_unblock(client, create_user):
    h1, u1 = _login(client, create_user, "blk1", "blk1@x.com")
    h2, u2 = _login(client, create_user, "blk2", "blk2@x.com")
    r = client.post(f"/api/users/{u1.id}/blocks/", json={"blocked_id": u2.id, "reason": "spam"}, headers=h1)
    assert r.status_code == 201
    assert r.json()["blocked_id"] == u2.id
    r = client.get(f"/api/users/{u1.id}/blocks/{u2.id}/status", headers=h1)
    assert r.status_code == 200
    assert r.json()["blocked"] is True
    r = client.get(f"/api/users/{u1.id}/blocks/", headers=h1)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    r = client.delete(f"/api/users/{u1.id}/blocks/{u2.id}", headers=h1)
    assert r.status_code == 200
    r = client.get(f"/api/users/{u1.id}/blocks/{u2.id}/status", headers=h1)
    assert r.json()["blocked"] is False


def test_block_forbidden_for_other_user(client, create_user):
    h1, u1 = _login(client, create_user, "bbb1", "o1@x.com")
    h2, u2 = _login(client, create_user, "bbb2", "o2@x.com")
    h3, u3 = _login(client, create_user, "bbb3", "o3@x.com")
    r = client.post(f"/api/users/{u1.id}/blocks/", json={"blocked_id": u2.id}, headers=h3)
    assert r.status_code == 403
