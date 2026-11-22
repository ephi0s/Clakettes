"""Tests for festival CRUD endpoints."""


class TestListFestivals:
    """Tests for GET /api/festivals/."""

    def test_list_empty(self, client):
        response = client.get("/api/festivals/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_festivals(self, client, auth_headers):
        headers, _ = auth_headers
        client.post("/api/festivals/", json={"name": "Fest 1"}, headers=headers)
        client.post("/api/festivals/", json={"name": "Fest 2"}, headers=headers)
        response = client.get("/api/festivals/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2


class TestCreateFestival:
    """Tests for POST /api/festivals/."""

    def test_create_success(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/festivals/",
            json={
                "name": "Sundance",
                "description": "Film festival",
                "location": "Utah",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sundance"
        assert data["is_active"] is True

    def test_create_requires_auth(self, client):
        response = client.post("/api/festivals/", json={"name": "No Auth"})
        assert response.status_code == 401


class TestGetFestival:
    """Tests for GET /api/festivals/{id}."""

    def test_get_success(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/festivals/", json={"name": "Test"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.get(f"/api/festivals/{fest_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test"

    def test_get_not_found(self, client):
        response = client.get("/api/festivals/9999")
        assert response.status_code == 404


class TestUpdateFestival:
    """Tests for PUT /api/festivals/{id}."""

    def test_update_success(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Old"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.put(f"/api/festivals/{fest_id}", json={"name": "New"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "New"

    def test_update_requires_auth(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.put(f"/api/festivals/{fest_id}", json={"name": "Hacked"})
        assert response.status_code == 401


class TestDeleteFestival:
    """Tests for DELETE /api/festivals/{id}."""

    def test_delete_success(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Doomed"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.delete(f"/api/festivals/{fest_id}", headers=headers)
        assert response.status_code == 200
        get_resp = client.get(f"/api/festivals/{fest_id}")
        assert get_resp.status_code == 404

    def test_delete_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.delete(f"/api/festivals/{fest_id}")
        assert response.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/festivals/9999", headers=headers)
        assert response.status_code == 404


class TestFestivalLocations:
    """Tests for festival-location association endpoints."""

    def _create_location(self, client, headers, name="Lugar"):
        response = client.post(
            "/api/locations/",
            json={"name": name, "latitude": 40.0, "longitude": -3.7},
            headers=headers,
        )
        return response.json()["id"]

    def test_list_empty(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.get(f"/api/festivals/{fest_id}/locations")
        assert response.status_code == 200
        assert response.json() == []

    def test_add_and_list(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)

        add_resp = client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)
        assert add_resp.status_code == 201
        assert add_resp.json()["id"] == loc_id

        list_resp = client.get(f"/api/festivals/{fest_id}/locations")
        assert list_resp.status_code == 200
        assert [loc["id"] for loc in list_resp.json()] == [loc_id]

    def test_add_duplicate_conflict(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)
        client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)
        dup = client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)
        assert dup.status_code == 409

    def test_add_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)
        response = client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id})
        assert response.status_code == 401

    def test_add_forbidden_for_regular_user(self, client, auth_headers, admin_headers):
        admin, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=admin)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, admin)
        user_headers, _ = auth_headers
        response = client.post(
            f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=user_headers
        )
        assert response.status_code == 403

    def test_remove(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)
        client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)

        del_resp = client.delete(f"/api/festivals/{fest_id}/locations/{loc_id}", headers=headers)
        assert del_resp.status_code == 200

        list_resp = client.get(f"/api/festivals/{fest_id}/locations")
        assert list_resp.json() == []


class TestFestivalMediaUrls:
    """Relative upload paths and absolute URLs must both round-trip."""

    def test_create_with_relative_media(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/festivals/",
            json={
                "name": "Media Fest",
                "logo_url": "/uploads/festivals/logo.png",
                "banner_url": "/uploads/festivals/banner.png",
                "website": "https://example.com",
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["logo_url"] == "/uploads/festivals/logo.png"
        assert response.json()["banner_url"] == "/uploads/festivals/banner.png"

    def test_update_and_read_relative_media(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = client.post("/api/festivals/", json={"name": "Media Fest"}, headers=headers).json()["id"]
        updated = client.put(
            f"/api/festivals/{fest_id}",
            json={"banner_url": "/uploads/festivals/banner.png"},
            headers=headers,
        )
        assert updated.status_code == 200
        assert client.get(f"/api/festivals/{fest_id}").json()["banner_url"] == "/uploads/festivals/banner.png"

    def test_rejects_invalid_url(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.put(
            f"/api/festivals/{client.post('/api/festivals/', json={'name': 'F'}, headers=headers).json()['id']}",
            json={"logo_url": "not-a-url"},
            headers=headers,
        )
        assert response.status_code == 422


class TestFestivalShortFilms:
    """Short films live inside their festival."""

    def test_create_and_list_nested(self, client, auth_headers, festival_id):
        headers, _ = auth_headers
        created = client.post(
            f"/api/festivals/{festival_id}/shortfilms",
            json={"title": "Express Film", "contest_type": "contest"},
            headers=headers,
        )
        assert created.status_code == 201
        assert created.json()["festival_id"] == festival_id
        assert created.json()["contest_type"] == "contest"
        listed = client.get(f"/api/festivals/{festival_id}/shortfilms")
        assert listed.status_code == 200
        assert [film["title"] for film in listed.json()["items"]] == ["Express Film"]

    def test_filter_by_contest_type(self, client, auth_headers, festival_id):
        headers, _ = auth_headers
        client.post(f"/api/festivals/{festival_id}/shortfilms", json={"title": "Official"}, headers=headers)
        client.post(
            f"/api/festivals/{festival_id}/shortfilms",
            json={"title": "Contest", "contest_type": "contest"},
            headers=headers,
        )
        response = client.get(f"/api/festivals/{festival_id}/shortfilms?contest_type=contest")
        assert response.status_code == 200
        assert [film["title"] for film in response.json()["items"]] == ["Contest"]

    def test_detail_includes_shortfilms(self, client, auth_headers, festival_id):
        headers, _ = auth_headers
        client.post(f"/api/festivals/{festival_id}/shortfilms", json={"title": "Film"}, headers=headers)
        detail = client.get(f"/api/festivals/{festival_id}").json()
        assert detail["shortfilm_count"] == 1
        assert [film["title"] for film in detail["shortfilms"]] == ["Film"]

    def test_cross_festival_shortfilm_is_not_found(self, client, auth_headers, festival_id, db_session):
        from app.models.festival import Festival

        headers, _ = auth_headers
        other = Festival(name="Other Festival")
        db_session.add(other)
        db_session.commit()
        film = client.post(f"/api/festivals/{festival_id}/shortfilms", json={"title": "Film"}, headers=headers).json()
        assert client.get(f"/api/festivals/{other.id}/shortfilms/{film['id']}").status_code == 404

    def test_create_festival_without_shortfilms_is_fine(self, client, admin_headers):
        headers, _ = admin_headers
        festival = client.post("/api/festivals/", json={"name": "First Festival"}, headers=headers).json()
        assert client.get(f"/api/festivals/{festival['id']}").json()["shortfilm_count"] == 0
