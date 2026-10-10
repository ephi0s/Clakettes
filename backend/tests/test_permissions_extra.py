def _create_festival(db_session):
    from app.models.festival import Festival

    fest = Festival(name="Perm Festival", is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    return fest


def test_committee_create_requires_auth(client, db_session):
    fest = _create_festival(db_session)
    resp = client.post(
        f"/api/festivals/{fest.id}/committees/",
        json={"festival_id": fest.id, "name": "Test Committee"},
    )
    assert resp.status_code == 401


def test_location_create_requires_auth(client):
    resp = client.post(
        "/api/locations/",
        json={"name": "No Auth Loc", "latitude": 1.0, "longitude": 1.0},
    )
    assert resp.status_code == 401


def test_festival_role_assign_requires_admin(client, db_session, auth_headers):
    fest = _create_festival(db_session)
    headers, _ = auth_headers
    resp = client.post(
        f"/api/festivals/{fest.id}/roles/",
        json={"festival_id": fest.id, "role_id": 1},
        headers=headers,
    )
    assert resp.status_code == 403
