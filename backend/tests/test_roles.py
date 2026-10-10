"""Comprehensive tests for roles, tags, groups, committees, delegations, transitions."""


class TestRolesList:
    """Tests for GET /api/roles/."""

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/roles/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_roles(self, client, admin_headers):
        headers, _ = admin_headers
        client.post("/api/roles/", json={"name": "admin", "display_name": "Admin"}, headers=headers)
        client.post("/api/roles/", json={"name": "user", "display_name": "User"}, headers=headers)
        response = client.get("/api/roles/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_list_requires_auth(self, client):
        response = client.get("/api/roles/")
        assert response.status_code == 401

    def test_list_filter_by_scope(self, client, admin_headers):
        headers, _ = admin_headers
        client.post(
            "/api/roles/", json={"name": "global_role", "display_name": "Global", "scope": "global"}, headers=headers
        )  # noqa: E501
        client.post(
            "/api/roles/", json={"name": "fest_role", "display_name": "Fest", "scope": "festival"}, headers=headers
        )  # noqa: E501
        response = client.get("/api/roles/?scope=global", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "global_role"

    def test_list_pagination(self, client, admin_headers):
        headers, _ = admin_headers
        for i in range(5):
            client.post("/api/roles/", json={"name": f"role{i}", "display_name": f"Role {i}"}, headers=headers)
        response = client.get("/api/roles/?page=1&size=2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 2


class TestRolesCreate:
    """Tests for POST /api/roles/."""

    def test_create_success(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/roles/",
            json={
                "name": "moderator",
                "display_name": "Moderator",
                "description": "Can moderate content",
                "scope": "global",
                "hierarchy_level": 5,
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "moderator"
        assert data["display_name"] == "Moderator"
        assert data["scope"] == "global"
        assert data["hierarchy_level"] == 5
        assert data["is_active"] is True

    def test_create_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post("/api/roles/", json={"name": "user_role", "display_name": "User Role"}, headers=headers)
        assert response.status_code == 403

    def test_create_requires_auth(self, client):
        response = client.post("/api/roles/", json={"name": "anon", "display_name": "Anon"})
        assert response.status_code == 401

    def test_create_duplicate_name(self, client, admin_headers):
        headers, _ = admin_headers
        client.post("/api/roles/", json={"name": "dupe", "display_name": "First"}, headers=headers)
        response = client.post("/api/roles/", json={"name": "dupe", "display_name": "Second"}, headers=headers)
        assert response.status_code == 400
        assert "already exists" in response.text.lower()


class TestRolesGet:
    """Tests for GET /api/roles/{role_id}."""

    def test_get_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "viewer", "display_name": "Viewer"}, headers=headers)
        role_id = create.json()["id"]
        response = client.get(f"/api/roles/{role_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "viewer"

    def test_get_not_found(self, client):
        response = client.get("/api/roles/9999")
        assert response.status_code == 404

    def test_get_no_auth_required(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "pub", "display_name": "Public"}, headers=headers)
        role_id = create.json()["id"]
        response = client.get(f"/api/roles/{role_id}")
        assert response.status_code == 200


class TestRolesUpdate:
    """Tests for PUT /api/roles/{role_id}."""

    def test_update_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "oldname", "display_name": "Old"}, headers=headers)
        role_id = create.json()["id"]
        response = client.put(f"/api/roles/{role_id}", json={"display_name": "Updated"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["display_name"] == "Updated"
        assert response.json()["name"] == "oldname"

    def test_update_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "restricted", "display_name": "Restricted"}, headers=admin_h)
        role_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.put(f"/api/roles/{role_id}", json={"display_name": "Hacked"}, headers=user_h)
        assert response.status_code == 403

    def test_update_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "noauth", "display_name": "No Auth"}, headers=headers)
        role_id = create.json()["id"]
        response = client.put(f"/api/roles/{role_id}", json={"display_name": "X"})
        assert response.status_code == 401

    def test_update_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.put("/api/roles/9999", json={"display_name": "Ghost"}, headers=headers)
        assert response.status_code == 404


class TestRolesDelete:
    """Tests for DELETE /api/roles/{role_id}."""

    def test_delete_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "delete_me", "display_name": "Delete Me"}, headers=headers)
        role_id = create.json()["id"]
        response = client.delete(f"/api/roles/{role_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Role deleted"
        get_resp = client.get(f"/api/roles/{role_id}")
        assert get_resp.status_code == 404

    def test_delete_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "admin_only", "display_name": "Admin Only"}, headers=admin_h)
        role_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.delete(f"/api/roles/{role_id}", headers=user_h)
        assert response.status_code == 403

    def test_delete_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post("/api/roles/", json={"name": "r", "display_name": "R"}, headers=headers)
        role_id = create.json()["id"]
        response = client.delete(f"/api/roles/{role_id}")
        assert response.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/roles/9999", headers=headers)
        assert response.status_code == 404


class TestRolesHierarchy:
    """Tests for GET /api/roles/hierarchy/."""

    def test_hierarchy_empty(self, client):
        response = client.get("/api/roles/hierarchy/")
        assert response.status_code == 200
        assert response.json() == []

    def test_hierarchy_with_roles(self, client, admin_headers):
        headers, _ = admin_headers
        client.post("/api/roles/", json={"name": "a", "display_name": "A", "hierarchy_level": 1}, headers=headers)
        client.post("/api/roles/", json={"name": "b", "display_name": "B", "hierarchy_level": 2}, headers=headers)
        response = client.get("/api/roles/hierarchy/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        levels = [r["hierarchy_level"] for r in data]
        assert levels == sorted(levels, reverse=True)

    def test_hierarchy_no_auth_required(self, client):
        response = client.get("/api/roles/hierarchy/")
        assert response.status_code == 200


class TestFestivalRolesList:
    """Tests for GET /api/festivals/{festival_id}/roles/."""

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "TestFest"}, headers=headers).json()
        response = client.get(f"/api/festivals/{fest['id']}/roles/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_roles(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "jury", "display_name": "Jury"}, headers=admin_h).json()
        fest = client.post("/api/festivals/", json={"name": "Venice"}, headers=user_h).json()
        client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        response = client.get(f"/api/festivals/{fest['id']}/roles/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_list_festival_not_found(self, client):
        response = client.get("/api/festivals/9999/roles/")
        assert response.status_code == 404

    def test_list_no_auth_required(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.get(f"/api/festivals/{fest['id']}/roles/")
        assert response.status_code == 200


class TestFestivalRolesCreate:
    """Tests for POST /api/festivals/{festival_id}/roles/."""

    def test_create_success(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "tech", "display_name": "Tech"}, headers=admin_h).json()
        fest = client.post("/api/festivals/", json={"name": "Cannes"}, headers=user_h).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role_id"] == role["id"]
        assert data["festival_id"] == fest["id"]

    def test_create_requires_auth(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "x", "display_name": "X"}, headers=admin_h).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
        )
        assert response.status_code == 401

    def test_create_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/festivals/9999/roles/",
            json={
                "role_id": 1,
                "festival_id": 9999,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_create_role_not_found(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=admin_h).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": 9999,
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 404


class TestFestivalRolesInitialize:
    """Tests for POST /api/festivals/{festival_id}/roles/initialize."""

    def test_initialize_success(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "InitFest"}, headers=user_h).json()
        response = client.post(f"/api/festivals/{fest['id']}/roles/initialize", headers=admin_h)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_initialize_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.post(f"/api/festivals/{fest['id']}/roles/initialize", headers=headers)
        assert response.status_code == 403

    def test_initialize_requires_auth(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.post(f"/api/festivals/{fest['id']}/roles/initialize")
        assert response.status_code == 401

    def test_initialize_festival_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post("/api/festivals/9999/roles/initialize", headers=headers)
        assert response.status_code == 404


class TestFestivalRolesUpdate:
    """Tests for PUT /api/festivals/{festival_id}/roles/{fr_id}."""

    def test_update_success(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post(
            "/api/roles/", json={"name": "volunteer", "display_name": "Volunteer"}, headers=admin_h
        ).json()  # noqa: E501
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fr = client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.put(
            f"/api/festivals/{fest['id']}/roles/{fr['id']}",
            json={
                "max_assignees": 10,
            },
            headers=admin_h,
        )
        assert response.status_code == 200
        assert response.json()["max_assignees"] == 10

    def test_update_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put("/api/festivals/9999/roles/1", json={"max_assignees": 5}, headers=headers)
        assert response.status_code == 404

    def test_update_festival_role_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.put(f"/api/festivals/{fest['id']}/roles/9999", json={"max_assignees": 5}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "v2", "display_name": "V2"}, headers=admin_h).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fr = client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.put(f"/api/festivals/{fest['id']}/roles/{fr['id']}", json={"max_assignees": 5})
        assert response.status_code == 401


class TestFestivalRolesDelete:
    """Tests for DELETE /api/festivals/{festival_id}/roles/{fr_id}."""

    def test_delete_success(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "temp", "display_name": "Temp"}, headers=admin_h).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fr = client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/festivals/{fest['id']}/roles/{fr['id']}", headers=admin_h)
        assert response.status_code == 200
        assert response.json()["message"] == "Festival role removed"

    def test_delete_requires_auth(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "t", "display_name": "T"}, headers=admin_h).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fr = client.post(
            f"/api/festivals/{fest['id']}/roles/",
            json={
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/festivals/{fest['id']}/roles/{fr['id']}")
        assert response.status_code == 401

    def test_delete_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.delete(f"/api/festivals/{fest['id']}/roles/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/festivals/9999/roles/1", headers=headers)
        assert response.status_code == 404


class TestParticipantTagsList:
    """Tests for GET /api/participant-tags/."""

    def test_list_empty(self, client):
        response = client.get("/api/participant-tags/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_tags(self, client, admin_headers):
        headers, _ = admin_headers
        client.post(
            "/api/participant-tags/",
            json={
                "name": "director",
                "display_name": "Director",
                "category": "direction",
            },
            headers=headers,
        )
        response = client.get("/api/participant-tags/")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_no_auth_required(self, client):
        response = client.get("/api/participant-tags/")
        assert response.status_code == 200

    def test_list_filter_by_category(self, client, admin_headers):
        headers, _ = admin_headers
        client.post(
            "/api/participant-tags/",
            json={
                "name": "actor",
                "display_name": "Actor",
                "category": "acting",
            },
            headers=headers,
        )
        client.post(
            "/api/participant-tags/",
            json={
                "name": "director2",
                "display_name": "Director",
                "category": "direction",
            },
            headers=headers,
        )
        response = client.get("/api/participant-tags/?category=acting")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "actor"


class TestParticipantTagsCreate:
    """Tests for POST /api/participant-tags/."""

    def test_create_success(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/participant-tags/",
            json={
                "name": "sound_engineer",
                "display_name": "Sound Engineer",
                "category": "sound",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "sound_engineer"
        assert data["category"] == "sound"
        assert data["is_active"] is True

    def test_create_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/participant-tags/",
            json={
                "name": "editor",
                "display_name": "Editor",
                "category": "editing",
            },
            headers=headers,
        )
        assert response.status_code == 403

    def test_create_requires_auth(self, client):
        response = client.post(
            "/api/participant-tags/",
            json={
                "name": "anon",
                "display_name": "Anon",
                "category": "other",
            },
        )
        assert response.status_code == 401

    def test_create_duplicate_name(self, client, admin_headers):
        headers, _ = admin_headers
        client.post(
            "/api/participant-tags/",
            json={
                "name": "camera_op",
                "display_name": "Camera Op",
                "category": "camera",
            },
            headers=headers,
        )
        response = client.post(
            "/api/participant-tags/",
            json={
                "name": "camera_op",
                "display_name": "Camera Operator",
                "category": "camera",
            },
            headers=headers,
        )
        assert response.status_code == 400


class TestParticipantTagsGet:
    """Tests for GET /api/participant-tags/{tag_id}."""

    def test_get_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/participant-tags/",
            json={
                "name": "vfx_artist",
                "display_name": "VFX Artist",
                "category": "vfx",
            },
            headers=headers,
        )
        tag_id = create.json()["id"]
        response = client.get(f"/api/participant-tags/{tag_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "vfx_artist"

    def test_get_not_found(self, client):
        response = client.get("/api/participant-tags/9999")
        assert response.status_code == 404

    def test_get_no_auth_required(self, client):
        response = client.get("/api/participant-tags/1")
        assert response.status_code == 404  # doesn't exist


class TestParticipantTagsUpdate:
    """Tests for PUT /api/participant-tags/{tag_id}."""

    def test_update_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/participant-tags/",
            json={
                "name": "lighting_tech",
                "display_name": "Lighting Tech",
                "category": "lighting",
            },
            headers=headers,
        )
        tag_id = create.json()["id"]
        response = client.put(
            f"/api/participant-tags/{tag_id}",
            json={
                "display_name": "Senior Lighting Tech",
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "Senior Lighting Tech"

    def test_update_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post(
            "/api/participant-tags/",
            json={
                "name": "makeup",
                "display_name": "Makeup",
                "category": "makeup",
            },
            headers=admin_h,
        )
        tag_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.put(f"/api/participant-tags/{tag_id}", json={"display_name": "Hacked"}, headers=user_h)
        assert response.status_code == 403

    def test_update_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.put("/api/participant-tags/9999", json={"display_name": "Ghost"}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/participant-tags/",
            json={
                "name": "props_master",
                "display_name": "Props",
                "category": "props",
            },
            headers=headers,
        )
        tag_id = create.json()["id"]
        response = client.put(f"/api/participant-tags/{tag_id}", json={"display_name": "X"})
        assert response.status_code == 401


class TestParticipantTagsDelete:
    """Tests for DELETE /api/participant-tags/{tag_id}."""

    def test_delete_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/participant-tags/",
            json={
                "name": "costume_design",
                "display_name": "Costume",
                "category": "costume",
            },
            headers=headers,
        )
        tag_id = create.json()["id"]
        response = client.delete(f"/api/participant-tags/{tag_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Tag deleted"
        get_resp = client.get(f"/api/participant-tags/{tag_id}")
        assert get_resp.status_code == 404

    def test_delete_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post(
            "/api/participant-tags/",
            json={
                "name": "art_director",
                "display_name": "Art",
                "category": "art",
            },
            headers=admin_h,
        )
        tag_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.delete(f"/api/participant-tags/{tag_id}", headers=user_h)
        assert response.status_code == 403

    def test_delete_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/participant-tags/9999", headers=headers)
        assert response.status_code == 404


class TestFestivalParticipantTagsList:
    """Tests for GET /api/festivals/{festival_id}/participant-tags/."""

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.get(f"/api/festivals/{fest['id']}/participant-tags/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_with_tags(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "writer",
                "display_name": "Writer",
                "category": "writing",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        response = client.get(f"/api/festivals/{fest['id']}/participant-tags/")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_festival_not_found(self, client):
        response = client.get("/api/festivals/9999/participant-tags/")
        assert response.status_code == 404


class TestFestivalParticipantTagsCreate:
    """Tests for POST /api/festivals/{festival_id}/participant-tags/."""

    def test_create_success(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "dp",
                "display_name": "DP",
                "category": "camera",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 201
        assert response.json()["tag_id"] == tag["id"]

    def test_create_duplicate(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "gaffer",
                "display_name": "Gaffer",
                "category": "lighting",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        response = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 400
        assert "already configured" in response.text.lower()

    def test_create_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/festivals/9999/participant-tags/",
            json={
                "tag_id": 1,
                "festival_id": 9999,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_create_tag_not_found(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=admin_h).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": 9999,
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 404

    def test_create_requires_auth(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "boom_op",
                "display_name": "Boom Op",
                "category": "sound",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
        )
        assert response.status_code == 401


class TestFestivalParticipantTagsUpdate:
    """Tests for PUT /api/festivals/{festival_id}/participant-tags/{fpt_id}."""

    def test_update_success(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "producer",
                "display_name": "Producer",
                "category": "production",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fpt = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.put(
            f"/api/festivals/{fest['id']}/participant-tags/{fpt['id']}",
            json={
                "is_required": True,
            },
            headers=admin_h,
        )
        assert response.status_code == 200
        assert response.json()["is_required"] is True

    def test_update_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.put(
            f"/api/festivals/{fest['id']}/participant-tags/9999",
            json={
                "is_required": True,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_update_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put(
            "/api/festivals/9999/participant-tags/1",
            json={
                "is_required": True,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_update_requires_auth(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "editor2",
                "display_name": "Editor",
                "category": "editing",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fpt = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.put(
            f"/api/festivals/{fest['id']}/participant-tags/{fpt['id']}",
            json={
                "is_required": True,
            },
        )
        assert response.status_code == 401


class TestFestivalParticipantTagsDelete:
    """Tests for DELETE /api/festivals/{festival_id}/participant-tags/{fpt_id}."""

    def test_delete_success(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "score",
                "display_name": "Composer",
                "category": "music",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fpt = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/festivals/{fest['id']}/participant-tags/{fpt['id']}", headers=admin_h)
        assert response.status_code == 200
        assert response.json()["message"] == "Festival tag removed"

    def test_delete_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.delete(f"/api/festivals/{fest['id']}/participant-tags/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_requires_auth(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "colorist",
                "display_name": "Colorist",
                "category": "post_production",
            },
            headers=admin_h,
        ).json()
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        fpt = client.post(
            f"/api/festivals/{fest['id']}/participant-tags/",
            json={
                "tag_id": tag["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/festivals/{fest['id']}/participant-tags/{fpt['id']}")
        assert response.status_code == 401


class TestUserRolesList:
    """Tests for GET /api/users/{user_id}/roles/."""

    def test_list_empty(self, client, auth_headers):
        headers, user = auth_headers
        response = client.get(f"/api/users/{user.id}/roles/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_roles(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "member", "display_name": "Member"}, headers=admin_h).json()
        client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        )
        response = client.get(f"/api/users/{user.id}/roles/", headers=user_h)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["role_id"] == role["id"]

    def test_list_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/users/9999/roles/", headers=headers)
        assert response.status_code == 404

    def test_list_requires_auth(self, client, auth_headers):
        headers, user = auth_headers
        response = client.get(f"/api/users/{user.id}/roles/")
        assert response.status_code == 401


class TestUserRolesAssign:
    """Tests for POST /api/users/{user_id}/roles/."""

    def test_assign_success(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "helper", "display_name": "Helper"}, headers=admin_h).json()
        response = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 201
        assert response.json()["role_id"] == role["id"]
        assert response.json()["user_id"] == user.id

    def test_assign_duplicate(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "double", "display_name": "Double"}, headers=admin_h).json()
        client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        )
        response = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 400
        assert "already has this role" in response.text.lower()

    def test_assign_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/users/9999/roles/",
            json={
                "user_id": 9999,
                "role_id": 1,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_assign_role_not_found(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        response = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": 9999,
            },
            headers=admin_h,
        )
        assert response.status_code == 404

    def test_assign_requires_auth(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "auth_test", "display_name": "Auth"}, headers=admin_h).json()
        response = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
        )
        assert response.status_code == 401

    def test_assign_with_festival_scope(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, user = auth_headers
        role = client.post(
            "/api/roles/",
            json={"name": "fest_role2", "display_name": "Fest Role", "scope": "festival"},
            headers=admin_h,
        ).json()  # noqa: E501
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=user_h).json()
        response = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
                "festival_id": fest["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 201
        assert response.json()["festival_id"] == fest["id"]


class TestUserRolesUpdate:
    """Tests for PUT /api/users/{user_id}/roles/{ur_id}."""

    def test_update_success(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post(
            "/api/roles/", json={"name": "updatable", "display_name": "Updatable"}, headers=admin_h
        ).json()  # noqa: E501
        ur = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        ).json()
        response = client.put(
            f"/api/users/{user.id}/roles/{ur['id']}",
            json={
                "status": "active",
            },
            headers=admin_h,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_update_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put("/api/users/9999/roles/1", json={"status": "active"}, headers=headers)
        assert response.status_code == 404

    def test_update_user_role_not_found(self, client, auth_headers):
        headers, user = auth_headers
        response = client.put(f"/api/users/{user.id}/roles/9999", json={"status": "active"}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "u", "display_name": "U"}, headers=admin_h).json()
        ur = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        ).json()
        response = client.put(f"/api/users/{user.id}/roles/{ur['id']}", json={"status": "active"})
        assert response.status_code == 401


class TestUserRolesRemove:
    """Tests for DELETE /api/users/{user_id}/roles/{ur_id}."""

    def test_remove_success(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "remove_me", "display_name": "Remove"}, headers=admin_h).json()
        ur = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/users/{user.id}/roles/{ur['id']}", headers=admin_h)
        assert response.status_code == 200
        assert response.json()["message"] == "Role removed from user"

    def test_remove_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/users/9999/roles/1", headers=headers)
        assert response.status_code == 404

    def test_remove_user_role_not_found(self, client, auth_headers):
        headers, user = auth_headers
        response = client.delete(f"/api/users/{user.id}/roles/9999", headers=headers)
        assert response.status_code == 404

    def test_remove_requires_auth(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "r2", "display_name": "R2"}, headers=admin_h).json()
        ur = client.post(
            f"/api/users/{user.id}/roles/",
            json={
                "user_id": user.id,
                "role_id": role["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/users/{user.id}/roles/{ur['id']}")
        assert response.status_code == 401


class TestUserParticipantTagsList:
    """Tests for GET /api/users/{user_id}/participant-tags/."""

    def test_list_empty(self, client, auth_headers):
        headers, user = auth_headers
        response = client.get(f"/api/users/{user.id}/participant-tags/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_with_tags(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "actor1",
                "display_name": "Actor",
                "category": "acting",
            },
            headers=admin_h,
        ).json()
        client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": tag["id"],
            },
            headers=admin_h,
        )
        response = client.get(f"/api/users/{user.id}/participant-tags/", headers=user_h)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/users/9999/participant-tags/", headers=headers)
        assert response.status_code == 404


class TestUserParticipantTagsAssign:
    """Tests for POST /api/users/{user_id}/participant-tags/."""

    def test_assign_success(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "director_tag",
                "display_name": "Director",
                "category": "direction",
            },
            headers=admin_h,
        ).json()
        response = client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": tag["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 201
        assert response.json()["tag_id"] == tag["id"]

    def test_assign_duplicate(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "dup_tag",
                "display_name": "Dup",
                "category": "other",
            },
            headers=admin_h,
        ).json()
        client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": tag["id"],
            },
            headers=admin_h,
        )
        response = client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": tag["id"],
            },
            headers=admin_h,
        )
        assert response.status_code == 400
        assert "already has this tag" in response.text.lower()

    def test_assign_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/users/9999/participant-tags/",
            json={
                "user_id": 9999,
                "tag_id": 1,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_assign_tag_not_found(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        response = client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": 9999,
            },
            headers=admin_h,
        )
        assert response.status_code == 404

    def test_assign_requires_auth(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "auth_tag",
                "display_name": "Auth",
                "category": "other",
            },
            headers=admin_h,
        ).json()
        response = client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": tag["id"],
            },
        )
        assert response.status_code == 401


class TestUserParticipantTagsRemove:
    """Tests for DELETE /api/users/{user_id}/participant-tags/{upt_id}."""

    def test_remove_success(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "remove_tag",
                "display_name": "Remove",
                "category": "other",
            },
            headers=admin_h,
        ).json()
        upt = client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": tag["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/users/{user.id}/participant-tags/{upt['id']}", headers=admin_h)
        assert response.status_code == 200
        assert response.json()["message"] == "Tag removed from user"

    def test_remove_not_found(self, client, auth_headers):
        headers, user = auth_headers
        response = client.delete(f"/api/users/{user.id}/participant-tags/9999", headers=headers)
        assert response.status_code == 404

    def test_remove_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/users/9999/participant-tags/1", headers=headers)
        assert response.status_code == 404

    def test_remove_requires_auth(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        tag = client.post(
            "/api/participant-tags/",
            json={
                "name": "remove_auth",
                "display_name": "RA",
                "category": "other",
            },
            headers=admin_h,
        ).json()
        upt = client.post(
            f"/api/users/{user.id}/participant-tags/",
            json={
                "user_id": user.id,
                "tag_id": tag["id"],
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/users/{user.id}/participant-tags/{upt['id']}")
        assert response.status_code == 401


class TestUserAliasesList:
    """Tests for GET /api/users/{user_id}/aliases/."""

    def test_list_empty(self, client, auth_headers):
        headers, user = auth_headers
        response = client.get(f"/api/users/{user.id}/aliases/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_aliases(self, client, auth_headers):
        headers, user = auth_headers
        client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "NickName",
            },
            headers=headers,
        )
        response = client.get(f"/api/users/{user.id}/aliases/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["alias"] == "NickName"

    def test_list_user_not_found(self, client):
        response = client.get("/api/users/9999/aliases/")
        assert response.status_code == 404

    def test_list_no_auth_required(self, client, auth_headers):
        headers, user = auth_headers
        response = client.get(f"/api/users/{user.id}/aliases/")
        assert response.status_code == 200

    def test_list_filter_by_context(self, client, auth_headers):
        headers, user = auth_headers
        client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "FilmName",
                "context": "shortfilm",
            },
            headers=headers,
        )
        client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "ChatName",
                "context": "chat",
            },
            headers=headers,
        )
        response = client.get(f"/api/users/{user.id}/aliases/?context=chat")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["alias"] == "ChatName"


class TestUserAliasesCreate:
    """Tests for POST /api/users/{user_id}/aliases/."""

    def test_create_success(self, client, auth_headers):
        headers, user = auth_headers
        response = client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "Pseudonym",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["alias"] == "Pseudonym"
        assert data["profile_token"] is not None

    def test_create_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/users/9999/aliases/",
            json={
                "user_id": 9999,
                "alias": "Ghost",
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_create_requires_auth(self, client, auth_headers):
        _, user = auth_headers
        response = client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "Anon",
            },
        )
        assert response.status_code == 401

    def test_create_with_explicit_profile_token(self, client, auth_headers):
        headers, user = auth_headers
        response = client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "TokenUser",
                "profile_token": "my-custom-token",
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["profile_token"] == "my-custom-token"


class TestUserAliasesUpdate:
    """Tests for PUT /api/users/{user_id}/aliases/{alias_id}."""

    def test_update_success(self, client, auth_headers):
        headers, user = auth_headers
        alias = client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "OldName",
            },
            headers=headers,
        ).json()
        response = client.put(
            f"/api/users/{user.id}/aliases/{alias['id']}",
            json={
                "alias": "NewName",
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["alias"] == "NewName"

    def test_update_not_found(self, client, auth_headers):
        headers, user = auth_headers
        response = client.put(
            f"/api/users/{user.id}/aliases/9999",
            json={
                "alias": "Ghost",
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_update_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put(
            "/api/users/9999/aliases/1",
            json={
                "alias": "X",
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_update_requires_auth(self, client, auth_headers):
        headers, user = auth_headers
        alias = client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "AuthTest",
            },
            headers=headers,
        ).json()
        response = client.put(
            f"/api/users/{user.id}/aliases/{alias['id']}",
            json={
                "alias": "NoAuth",
            },
        )
        assert response.status_code == 401


class TestUserAliasesDelete:
    """Tests for DELETE /api/users/{user_id}/aliases/{alias_id}."""

    def test_delete_success(self, client, auth_headers):
        headers, user = auth_headers
        alias = client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "DeleteMe",
            },
            headers=headers,
        ).json()
        response = client.delete(f"/api/users/{user.id}/aliases/{alias['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Alias deleted"

    def test_delete_not_found(self, client, auth_headers):
        headers, user = auth_headers
        response = client.delete(f"/api/users/{user.id}/aliases/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_user_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/users/9999/aliases/1", headers=headers)
        assert response.status_code == 404

    def test_delete_requires_auth(self, client, auth_headers):
        headers, user = auth_headers
        alias = client.post(
            f"/api/users/{user.id}/aliases/",
            json={
                "user_id": user.id,
                "alias": "AuthDelete",
            },
            headers=headers,
        ).json()
        response = client.delete(f"/api/users/{user.id}/aliases/{alias['id']}")
        assert response.status_code == 401


class TestValidationRulesList:
    """Tests for GET /api/validation-rules/."""

    def test_list_empty(self, client):
        response = client.get("/api/validation-rules/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_with_rules(self, client, admin_headers):
        headers, _ = admin_headers
        client.post(
            "/api/validation-rules/",
            json={
                "name": "full_name",
                "field_name": "full_name",
                "field_label": "Full Name",
                "is_required": True,
            },
            headers=headers,
        )
        response = client.get("/api/validation-rules/")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_no_auth_required(self, client):
        response = client.get("/api/validation-rules/")
        assert response.status_code == 200

    def test_list_filter_by_scope(self, client, admin_headers):
        headers, _ = admin_headers
        client.post(
            "/api/validation-rules/",
            json={
                "name": "global_field",
                "field_name": "g",
                "field_label": "G",
                "scope": "global",
            },
            headers=headers,
        )
        client.post(
            "/api/validation-rules/",
            json={
                "name": "festival_field",
                "field_name": "f",
                "field_label": "F",
                "scope": "festival",
            },
            headers=headers,
        )
        response = client.get("/api/validation-rules/?scope=festival")
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["name"] == "festival_field"


class TestValidationRulesCreate:
    """Tests for POST /api/validation-rules/."""

    def test_create_success(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/validation-rules/",
            json={
                "name": "bio_field",
                "field_name": "bio",
                "field_label": "Biography",
                "is_required": False,
                "max_length": 500,
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "bio_field"
        assert data["field_name"] == "bio"
        assert data["max_length"] == 500

    def test_create_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/validation-rules/",
            json={
                "name": "user_field",
                "field_name": "x",
                "field_label": "X",
            },
            headers=headers,
        )
        assert response.status_code == 403

    def test_create_requires_auth(self, client):
        response = client.post(
            "/api/validation-rules/",
            json={
                "name": "anon_field",
                "field_name": "a",
                "field_label": "A",
            },
        )
        assert response.status_code == 401


class TestValidationRulesGet:
    """Tests for GET /api/validation-rules/{rule_id}."""

    def test_get_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/validation-rules/",
            json={
                "name": "email_field",
                "field_name": "email",
                "field_label": "Email",
            },
            headers=headers,
        )
        rule_id = create.json()["id"]
        response = client.get(f"/api/validation-rules/{rule_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "email_field"

    def test_get_not_found(self, client):
        response = client.get("/api/validation-rules/9999")
        assert response.status_code == 404

    def test_get_no_auth_required(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/validation-rules/",
            json={
                "name": "public_rule",
                "field_name": "p",
                "field_label": "P",
            },
            headers=headers,
        )
        rule_id = create.json()["id"]
        response = client.get(f"/api/validation-rules/{rule_id}")
        assert response.status_code == 200


class TestValidationRulesUpdate:
    """Tests for PUT /api/validation-rules/{rule_id}."""

    def test_update_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/validation-rules/",
            json={
                "name": "phone_field",
                "field_name": "phone",
                "field_label": "Phone",
            },
            headers=headers,
        )
        rule_id = create.json()["id"]
        response = client.put(
            f"/api/validation-rules/{rule_id}",
            json={
                "is_required": True,
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["is_required"] is True

    def test_update_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post(
            "/api/validation-rules/",
            json={
                "name": "admin_rule",
                "field_name": "ar",
                "field_label": "AR",
            },
            headers=admin_h,
        )
        rule_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.put(f"/api/validation-rules/{rule_id}", json={"is_required": True}, headers=user_h)
        assert response.status_code == 403

    def test_update_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.put("/api/validation-rules/9999", json={"is_required": True}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/validation-rules/",
            json={
                "name": "noauth_rule",
                "field_name": "nr",
                "field_label": "NR",
            },
            headers=headers,
        )
        rule_id = create.json()["id"]
        response = client.put(f"/api/validation-rules/{rule_id}", json={"is_required": True})
        assert response.status_code == 401


class TestValidationRulesDelete:
    """Tests for DELETE /api/validation-rules/{rule_id}."""

    def test_delete_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/validation-rules/",
            json={
                "name": "delete_rule",
                "field_name": "dr",
                "field_label": "DR",
            },
            headers=headers,
        )
        rule_id = create.json()["id"]
        response = client.delete(f"/api/validation-rules/{rule_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Validation rule deleted"
        get_resp = client.get(f"/api/validation-rules/{rule_id}")
        assert get_resp.status_code == 404

    def test_delete_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post(
            "/api/validation-rules/",
            json={
                "name": "admin_del",
                "field_name": "ad",
                "field_label": "AD",
            },
            headers=admin_h,
        )
        rule_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.delete(f"/api/validation-rules/{rule_id}", headers=user_h)
        assert response.status_code == 403

    def test_delete_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/validation-rules/9999", headers=headers)
        assert response.status_code == 404


class TestValidationRuleGroupsList:
    """Tests for GET /api/validation-rule-groups/."""

    def test_list_empty(self, client):
        response = client.get("/api/validation-rule-groups/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_no_auth_required(self, client):
        response = client.get("/api/validation-rule-groups/")
        assert response.status_code == 200


class TestValidationRuleGroupsCreate:
    """Tests for POST /api/validation-rule-groups/."""

    def test_create_success(self, client, admin_headers):
        headers, _ = admin_headers
        rule = client.post(
            "/api/validation-rules/",
            json={
                "name": "grouped_rule",
                "field_name": "gr",
                "field_label": "GR",
            },
            headers=headers,
        ).json()
        response = client.post(
            "/api/validation-rule-groups/",
            json={
                "name": "Profile Group",
                "scope": "global",
                "rule_ids": [rule["id"]],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Profile Group"

    def test_create_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/validation-rule-groups/",
            json={
                "name": "User Group",
                "scope": "global",
            },
            headers=headers,
        )
        assert response.status_code == 403

    def test_create_requires_auth(self, client):
        response = client.post(
            "/api/validation-rule-groups/",
            json={
                "name": "Anon Group",
                "scope": "global",
            },
        )
        assert response.status_code == 401


class TestRoleGroupsList:
    """Tests for GET /api/role-groups/."""

    def test_list_empty(self, client):
        response = client.get("/api/role-groups/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_with_groups(self, client, admin_headers):
        headers, _ = admin_headers
        client.post("/api/role-groups/", json={"name": "technical", "display_name": "Technical"}, headers=headers)
        response = client.get("/api/role-groups/")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_no_auth_required(self, client):
        response = client.get("/api/role-groups/")
        assert response.status_code == 200

    def test_list_filter_active(self, client, admin_headers):
        headers, _ = admin_headers
        client.post(
            "/api/role-groups/",
            json={"name": "active_grp", "display_name": "Active", "is_active": True},
            headers=headers,
        )  # noqa: E501
        client.post(
            "/api/role-groups/",
            json={"name": "inactive_grp", "display_name": "Inactive", "is_active": False},
            headers=headers,
        )  # noqa: E501
        response = client.get("/api/role-groups/?is_active=true")
        assert response.status_code == 200
        assert response.json()["total"] == 1


class TestRoleGroupsCreate:
    """Tests for POST /api/role-groups/."""

    def test_create_success(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/role-groups/",
            json={
                "name": "direction",
                "display_name": "Direction",
                "description": "Direction roles",
                "sort_order": 1,
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "direction"
        assert data["display_name"] == "Direction"
        assert data["is_active"] is True

    def test_create_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/role-groups/",
            json={
                "name": "user_group",
                "display_name": "User Group",
            },
            headers=headers,
        )
        assert response.status_code == 403

    def test_create_requires_auth(self, client):
        response = client.post(
            "/api/role-groups/",
            json={
                "name": "anon",
                "display_name": "Anon",
            },
        )
        assert response.status_code == 401


class TestRoleGroupsGet:
    """Tests for GET /api/role-groups/{group_id}."""

    def test_get_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/role-groups/",
            json={
                "name": "creative",
                "display_name": "Creative",
            },
            headers=headers,
        )
        group_id = create.json()["id"]
        response = client.get(f"/api/role-groups/{group_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "creative"

    def test_get_not_found(self, client):
        response = client.get("/api/role-groups/9999")
        assert response.status_code == 404

    def test_get_no_auth_required(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/role-groups/",
            json={
                "name": "public_group",
                "display_name": "Public",
            },
            headers=headers,
        )
        group_id = create.json()["id"]
        response = client.get(f"/api/role-groups/{group_id}")
        assert response.status_code == 200


class TestRoleGroupsUpdate:
    """Tests for PUT /api/role-groups/{group_id}."""

    def test_update_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/role-groups/",
            json={
                "name": "old_group",
                "display_name": "Old",
            },
            headers=headers,
        )
        group_id = create.json()["id"]
        response = client.put(
            f"/api/role-groups/{group_id}",
            json={
                "display_name": "Updated Group",
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "Updated Group"

    def test_update_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post(
            "/api/role-groups/",
            json={
                "name": "admin_group",
                "display_name": "Admin Only",
            },
            headers=admin_h,
        )
        group_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.put(f"/api/role-groups/{group_id}", json={"display_name": "Hacked"}, headers=user_h)
        assert response.status_code == 403

    def test_update_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.put("/api/role-groups/9999", json={"display_name": "Ghost"}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/role-groups/",
            json={
                "name": "noauth_group",
                "display_name": "No Auth",
            },
            headers=headers,
        )
        group_id = create.json()["id"]
        response = client.put(f"/api/role-groups/{group_id}", json={"display_name": "X"})
        assert response.status_code == 401


class TestRoleGroupsDelete:
    """Tests for DELETE /api/role-groups/{group_id}."""

    def test_delete_success(self, client, admin_headers):
        headers, _ = admin_headers
        create = client.post(
            "/api/role-groups/",
            json={
                "name": "delete_group",
                "display_name": "Delete Me",
            },
            headers=headers,
        )
        group_id = create.json()["id"]
        response = client.delete(f"/api/role-groups/{group_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Role group deleted"
        get_resp = client.get(f"/api/role-groups/{group_id}")
        assert get_resp.status_code == 404

    def test_delete_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        create = client.post(
            "/api/role-groups/",
            json={
                "name": "admin_del_group",
                "display_name": "Admin Del",
            },
            headers=admin_h,
        )
        group_id = create.json()["id"]
        user_h, _ = auth_headers
        response = client.delete(f"/api/role-groups/{group_id}", headers=user_h)
        assert response.status_code == 403

    def test_delete_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/role-groups/9999", headers=headers)
        assert response.status_code == 404


class TestRoleGroupMembershipsList:
    """Tests for GET /api/role-groups/{group_id}/memberships/."""

    def test_list_empty(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "empty_group",
                "display_name": "Empty",
            },
            headers=headers,
        ).json()
        response = client.get(f"/api/role-groups/{group['id']}/memberships/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_group_not_found(self, client):
        response = client.get("/api/role-groups/9999/memberships/")
        assert response.status_code == 404

    def test_list_no_auth_required(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "pub_group",
                "display_name": "Public",
            },
            headers=headers,
        ).json()
        response = client.get(f"/api/role-groups/{group['id']}/memberships/")
        assert response.status_code == 200


class TestRoleGroupMembershipsCreate:
    """Tests for POST /api/role-groups/{group_id}/memberships/."""

    def test_create_success(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "mems",
                "display_name": "Memberships",
            },
            headers=headers,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "lead",
                "display_name": "Lead",
            },
            headers=headers,
        ).json()
        response = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
                "level": 1,
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role_id"] == role["id"]
        assert data["group_id"] == group["id"]
        assert data["level"] == 1

    def test_create_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "adm_mems",
                "display_name": "Admin Mems",
            },
            headers=admin_h,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "admin_lead",
                "display_name": "Admin Lead",
            },
            headers=admin_h,
        ).json()
        user_h, _ = auth_headers
        response = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
            },
            headers=user_h,
        )
        assert response.status_code == 403

    def test_create_group_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/role-groups/9999/memberships/",
            json={
                "group_id": 9999,
                "role_id": 1,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_create_role_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "no_role_group",
                "display_name": "No Role",
            },
            headers=headers,
        ).json()
        response = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": 9999,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_create_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "auth_mems",
                "display_name": "Auth Mems",
            },
            headers=headers,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "auth_lead",
                "display_name": "Auth Lead",
            },
            headers=headers,
        ).json()
        response = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
            },
        )
        assert response.status_code == 401


class TestRoleGroupMembershipsUpdate:
    """Tests for PUT /api/role-group-memberships/{membership_id}."""

    def test_update_success(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "upd_mems",
                "display_name": "Upd Mems",
            },
            headers=headers,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "upd_lead",
                "display_name": "Upd Lead",
            },
            headers=headers,
        ).json()
        mem = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
            },
            headers=headers,
        ).json()
        response = client.put(
            f"/api/role-group-memberships/{mem['id']}",
            json={
                "is_leader": True,
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["is_leader"] is True

    def test_update_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "admin_upd",
                "display_name": "Admin Upd",
            },
            headers=admin_h,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "admin_upd_role",
                "display_name": "Admin Upd Role",
            },
            headers=admin_h,
        ).json()
        mem = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
            },
            headers=admin_h,
        ).json()
        user_h, _ = auth_headers
        response = client.put(f"/api/role-group-memberships/{mem['id']}", json={"is_leader": True}, headers=user_h)
        assert response.status_code == 403

    def test_update_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.put("/api/role-group-memberships/9999", json={"is_leader": True}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "noauth_upd",
                "display_name": "No Auth Upd",
            },
            headers=headers,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "noauth_upd_role",
                "display_name": "No Auth Upd Role",
            },
            headers=headers,
        ).json()
        mem = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
            },
            headers=headers,
        ).json()
        response = client.put(f"/api/role-group-memberships/{mem['id']}", json={"is_leader": True})
        assert response.status_code == 401


class TestRoleGroupMembershipsDelete:
    """Tests for DELETE /api/role-group-memberships/{membership_id}."""

    def test_delete_success(self, client, admin_headers):
        headers, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "del_mems",
                "display_name": "Del Mems",
            },
            headers=headers,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "del_role",
                "display_name": "Del Role",
            },
            headers=headers,
        ).json()
        mem = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
            },
            headers=headers,
        ).json()
        response = client.delete(f"/api/role-group-memberships/{mem['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Membership deleted"

    def test_delete_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        group = client.post(
            "/api/role-groups/",
            json={
                "name": "admin_del_m",
                "display_name": "Admin Del M",
            },
            headers=admin_h,
        ).json()
        role = client.post(
            "/api/roles/",
            json={
                "name": "admin_del_r",
                "display_name": "Admin Del R",
            },
            headers=admin_h,
        ).json()
        mem = client.post(
            f"/api/role-groups/{group['id']}/memberships/",
            json={
                "group_id": group["id"],
                "role_id": role["id"],
            },
            headers=admin_h,
        ).json()
        user_h, _ = auth_headers
        response = client.delete(f"/api/role-group-memberships/{mem['id']}", headers=user_h)
        assert response.status_code == 403

    def test_delete_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/role-group-memberships/9999", headers=headers)
        assert response.status_code == 404


class TestCommitteesList:
    """Tests for GET /api/festivals/{festival_id}/committees/."""

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.get(f"/api/festivals/{fest['id']}/committees/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_with_committees(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Selection Committee",
            },
            headers=admin_h,
        )
        response = client.get(f"/api/festivals/{fest['id']}/committees/")
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_festival_not_found(self, client):
        response = client.get("/api/festivals/9999/committees/")
        assert response.status_code == 404

    def test_list_no_auth_required(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.get(f"/api/festivals/{fest['id']}/committees/")
        assert response.status_code == 200


class TestCommitteesCreate:
    """Tests for POST /api/festivals/{festival_id}/committees/."""

    def test_create_success(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Jury Committee",
            },
            headers=admin_h,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jury Committee"
        assert data["festival_id"] == fest["id"]

    def test_create_festival_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/festivals/9999/committees/",
            json={
                "festival_id": 9999,
                "name": "Ghost",
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_create_requires_auth(self, client, auth_headers):
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        response = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "No Auth",
            },
        )
        assert response.status_code == 401


class TestCommitteesGet:
    """Tests for GET /api/committees/{committee_id}."""

    def test_get_success(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        create = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Tech Committee",
            },
            headers=admin_h,
        ).json()
        response = client.get(f"/api/committees/{create['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Tech Committee"

    def test_get_not_found(self, client):
        response = client.get("/api/committees/9999")
        assert response.status_code == 404

    def test_get_no_auth_required(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        create = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Public Cmte",
            },
            headers=admin_h,
        ).json()
        response = client.get(f"/api/committees/{create['id']}")
        assert response.status_code == 200


class TestCommitteesUpdate:
    """Tests for PUT /api/committees/{committee_id}."""

    def test_update_success(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        create = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Old Name",
            },
            headers=admin_h,
        ).json()
        response = client.put(
            f"/api/committees/{create['id']}",
            json={
                "name": "New Name",
            },
            headers=admin_h,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    def test_update_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put("/api/committees/9999", json={"name": "Ghost"}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        create = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "No Auth Cmte",
            },
            headers=admin_h,
        ).json()
        response = client.put(f"/api/committees/{create['id']}", json={"name": "X"})
        assert response.status_code == 401


class TestCommitteesDelete:
    """Tests for DELETE /api/committees/{committee_id}."""

    def test_delete_success(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        create = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Delete Cmte",
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/committees/{create['id']}", headers=admin_h)
        assert response.status_code == 200
        assert response.json()["message"] == "Committee deleted"
        get_resp = client.get(f"/api/committees/{create['id']}")
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/committees/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_requires_auth(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        create = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Auth Cmte",
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/committees/{create['id']}")
        assert response.status_code == 401


class TestCommitteeMembersList:
    """Tests for GET /api/committees/{committee_id}/members/."""

    def test_list_empty(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Selection",
            },
            headers=admin_h,
        ).json()
        response = client.get(f"/api/committees/{cmte['id']}/members/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_committee_not_found(self, client):
        response = client.get("/api/committees/9999/members/")
        assert response.status_code == 404

    def test_list_no_auth_required(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        headers, _ = auth_headers
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Public",
            },
            headers=admin_h,
        ).json()
        response = client.get(f"/api/committees/{cmte['id']}/members/")
        assert response.status_code == 200


class TestCommitteeMembersAdd:
    """Tests for POST /api/committees/{committee_id}/members/."""

    def test_add_success(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        other_user, _ = create_user(username="member1", email="member1@test.com")
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Jury",
            },
            headers=admin_h,
        ).json()
        response = client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
            headers=admin_h,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == other_user.id
        assert data["role_in_committee"] == "member"

    def test_add_duplicate(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        other_user, _ = create_user(username="dup_mem", email="dup@test.com")
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Dup Cmte",
            },
            headers=admin_h,
        ).json()
        client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
            headers=admin_h,
        )
        response = client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
            headers=admin_h,
        )
        assert response.status_code == 400
        assert "already a member" in response.text.lower()

    def test_add_committee_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/committees/9999/members/",
            json={
                "committee_id": 9999,
                "user_id": 1,
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_add_requires_auth(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        other_user, _ = create_user(username="auth_mem", email="auth@test.com")
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Auth Cmte",
            },
            headers=admin_h,
        ).json()
        response = client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
        )
        assert response.status_code == 401


class TestCommitteeMembersUpdate:
    """Tests for PUT /api/committee-members/{member_id}."""

    def test_update_success(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        other_user, _ = create_user(username="upd_mem", email="upd@test.com")
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Upd Cmte",
            },
            headers=admin_h,
        ).json()
        mem = client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
            headers=admin_h,
        ).json()
        response = client.put(
            f"/api/committee-members/{mem['id']}",
            json={
                "role_in_committee": "chair",
            },
            headers=admin_h,
        )
        assert response.status_code == 200
        assert response.json()["role_in_committee"] == "chair"

    def test_update_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put(
            "/api/committee-members/9999",
            json={
                "role_in_committee": "chair",
            },
            headers=headers,
        )
        assert response.status_code == 404

    def test_update_requires_auth(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        other_user, _ = create_user(username="noauth_mem", email="noauth@test.com")
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "NoAuth Cmte",
            },
            headers=admin_h,
        ).json()
        mem = client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
            headers=admin_h,
        ).json()
        response = client.put(
            f"/api/committee-members/{mem['id']}",
            json={
                "role_in_committee": "chair",
            },
        )
        assert response.status_code == 401


class TestCommitteeMembersRemove:
    """Tests for DELETE /api/committee-members/{member_id}."""

    def test_remove_success(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        other_user, _ = create_user(username="del_mem", email="del@test.com")
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "Del Cmte",
            },
            headers=admin_h,
        ).json()
        mem = client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/committee-members/{mem['id']}", headers=admin_h)
        assert response.status_code == 200
        assert response.json()["message"] == "Member removed"

    def test_remove_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.delete("/api/committee-members/9999", headers=headers)
        assert response.status_code == 404

    def test_remove_requires_auth(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        headers, user = auth_headers
        other_user, _ = create_user(username="noauth_del", email="noauthdel@test.com")
        fest = client.post("/api/festivals/", json={"name": "F"}, headers=headers).json()
        cmte = client.post(
            f"/api/festivals/{fest['id']}/committees/",
            json={
                "festival_id": fest["id"],
                "name": "NoAuth Del",
            },
            headers=admin_h,
        ).json()
        mem = client.post(
            f"/api/committees/{cmte['id']}/members/",
            json={
                "committee_id": cmte["id"],
                "user_id": other_user.id,
            },
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/committee-members/{mem['id']}")
        assert response.status_code == 401


class TestDelegationsList:
    """Tests for GET /api/delegations/."""

    def test_list_empty(self, client):
        response = client.get("/api/delegations/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_no_auth_required(self, client):
        response = client.get("/api/delegations/")
        assert response.status_code == 200


class TestDelegationsCreate:
    """Tests for POST /api/delegations/."""

    def test_create_success(self, client, auth_headers, admin_headers, create_user):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="delegate", email="del@test.com")
        role = client.post(
            "/api/roles/", json={"name": "delegable", "display_name": "Delegable"}, headers=admin_h
        ).json()  # noqa: E501
        response = client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["delegator_id"] == user.id
        assert data["delegate_id"] == delegate.id
        assert data["role_id"] == role["id"]
        assert data["status"] == "active"

    def test_create_requires_auth(self, client, auth_headers, admin_headers, create_user):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="del2", email="del2@test.com")
        role = client.post("/api/roles/", json={"name": "del_role", "display_name": "Del Role"}, headers=admin_h).json()
        response = client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
        )
        assert response.status_code == 401


class TestDelegationsUpdate:
    """Tests for PUT /api/delegations/{delegation_id}."""

    def test_update_success(self, client, auth_headers, admin_headers, create_user):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="del_upd", email="delupd@test.com")
        role = client.post(
            "/api/roles/", json={"name": "del_upd_role", "display_name": "Del Upd"}, headers=admin_h
        ).json()  # noqa: E501
        delegation = client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=headers,
        ).json()
        response = client.put(
            f"/api/delegations/{delegation['id']}",
            json={
                "status": "expired",
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "expired"

    def test_update_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put("/api/delegations/9999", json={"status": "expired"}, headers=headers)
        assert response.status_code == 404

    def test_update_requires_auth(self, client, auth_headers, admin_headers, create_user):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="del_noauth", email="delnoauth@test.com")
        role = client.post(
            "/api/roles/", json={"name": "del_noauth_role", "display_name": "Del NoAuth"}, headers=admin_h
        ).json()  # noqa: E501
        delegation = client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=user_h,
        ).json()
        response = client.put(f"/api/delegations/{delegation['id']}", json={"status": "expired"})
        assert response.status_code == 401


class TestDelegationsRevoke:
    """Tests for POST /api/delegations/{delegation_id}/revoke."""

    def test_revoke_success(self, client, auth_headers, admin_headers, create_user):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="del_rev", email="delrev@test.com")
        role = client.post("/api/roles/", json={"name": "rev_role", "display_name": "Rev Role"}, headers=admin_h).json()
        delegation = client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=headers,
        ).json()
        response = client.post(f"/api/delegations/{delegation['id']}/revoke", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "revoked" or data.get("revoked_at") is not None

    def test_revoke_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post("/api/delegations/9999/revoke", headers=headers)
        assert response.status_code == 404

    def test_revoke_requires_auth(self, client, auth_headers, admin_headers, create_user):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="del_rev2", email="delrev2@test.com")
        role = client.post(
            "/api/roles/", json={"name": "rev_role2", "display_name": "Rev Role 2"}, headers=admin_h
        ).json()  # noqa: E501
        delegation = client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=user_h,
        ).json()
        response = client.post(f"/api/delegations/{delegation['id']}/revoke")
        assert response.status_code == 401

    def test_revoke_forbidden_for_outsider(self, client, auth_headers, admin_headers, create_user, db_session):
        from app.auth import create_session

        user_h, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="del_rev3", email="delrev3@test.com")
        outsider, _ = create_user(username="outsider_rev", email="outsiderrev@test.com")
        role = client.post(
            "/api/roles/", json={"name": "rev_role3", "display_name": "Rev Role 3"}, headers=admin_h
        ).json()
        delegation = client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=user_h,
        ).json()
        _, token, _ = create_session(db_session, outsider.id)
        response = client.post(
            f"/api/delegations/{delegation['id']}/revoke", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


class TestUserActiveDelegations:
    """Tests for GET /api/users/{user_id}/active-delegations."""

    def test_list_empty(self, client, auth_headers):
        headers, user = auth_headers
        response = client.get(f"/api/users/{user.id}/active-delegations")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_received(self, client, auth_headers, admin_headers, create_user):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="act_del", email="actdel@test.com")
        role = client.post("/api/roles/", json={"name": "act_role", "display_name": "Act Role"}, headers=admin_h).json()
        client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=headers,
        )
        response = client.get(f"/api/users/{delegate.id}/active-delegations?direction=received")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_given(self, client, auth_headers, admin_headers, create_user):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="act_given", email="actgiven@test.com")
        role = client.post(
            "/api/roles/", json={"name": "act_given_role", "display_name": "Act Given"}, headers=admin_h
        ).json()  # noqa: E501
        client.post(
            "/api/delegations/",
            json={
                "delegator_id": user.id,
                "delegate_id": delegate.id,
                "role_id": role["id"],
            },
            headers=headers,
        )
        response = client.get(f"/api/users/{user.id}/active-delegations?direction=given")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_no_auth_required(self, client, auth_headers):
        _, user = auth_headers
        response = client.get(f"/api/users/{user.id}/active-delegations")
        assert response.status_code == 200


class TestRoleTransitionsList:
    """Tests for GET /api/role-transitions/."""

    def test_list_requires_auth(self, client):
        response = client.get("/api/role-transitions/")
        assert response.status_code == 401

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/role-transitions/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_no_auth_required(self, client):
        """Role transitions stay closed: an anonymous read is rejected."""
        response = client.get("/api/role-transitions/")
        assert response.status_code == 401


class TestRoleTransitionsCreate:
    """Tests for POST /api/role-transitions/."""

    def test_create_success(self, client, auth_headers, admin_headers):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post(
            "/api/roles/", json={"name": "trans_role", "display_name": "Trans Role"}, headers=admin_h
        ).json()  # noqa: E501
        response = client.post(
            "/api/role-transitions/",
            json={
                "user_id": user.id,
                "to_role_id": role["id"],
                "transition_type": "creation",
                "changed_by": user.id,
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["to_role_id"] == role["id"]
        assert data["transition_type"] == "creation"

    def test_create_with_from_role(self, client, auth_headers, admin_headers):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        from_role = client.post(
            "/api/roles/", json={"name": "from_role", "display_name": "From"}, headers=admin_h
        ).json()  # noqa: E501
        to_role = client.post("/api/roles/", json={"name": "to_role", "display_name": "To"}, headers=admin_h).json()
        response = client.post(
            "/api/role-transitions/",
            json={
                "user_id": user.id,
                "from_role_id": from_role["id"],
                "to_role_id": to_role["id"],
                "transition_type": "promotion",
                "changed_by": user.id,
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["from_role_id"] == from_role["id"]
        assert response.json()["transition_type"] == "promotion"

    def test_create_requires_auth(self, client, auth_headers, admin_headers):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post(
            "/api/roles/", json={"name": "trans_noauth", "display_name": "Trans NoAuth"}, headers=admin_h
        ).json()  # noqa: E501
        response = client.post(
            "/api/role-transitions/",
            json={
                "user_id": user.id,
                "to_role_id": role["id"],
                "transition_type": "creation",
                "changed_by": user.id,
            },
        )
        assert response.status_code == 401


class TestUserRoleTransitions:
    """Tests for GET /api/users/{user_id}/role-transitions."""

    def test_list_requires_auth(self, client, auth_headers):
        _, user = auth_headers
        response = client.get(f"/api/users/{user.id}/role-transitions")
        assert response.status_code == 401

    def test_list_empty(self, client, auth_headers):
        headers, user = auth_headers
        response = client.get(f"/api/users/{user.id}/role-transitions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_with_transitions(self, client, auth_headers, admin_headers):
        headers, user = auth_headers
        admin_h, _ = admin_headers
        role = client.post(
            "/api/roles/", json={"name": "usr_trans", "display_name": "Usr Trans"}, headers=admin_h
        ).json()  # noqa: E501
        client.post(
            "/api/role-transitions/",
            json={
                "user_id": user.id,
                "to_role_id": role["id"],
                "transition_type": "creation",
                "changed_by": user.id,
            },
            headers=headers,
        )
        response = client.get(f"/api/users/{user.id}/role-transitions", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_user_not_found(self, client, admin_headers):
        admin_h, _ = admin_headers
        response = client.get("/api/users/9999/role-transitions", headers=admin_h)
        assert response.status_code == 404

    def test_list_forbidden_for_other_users(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/users/9999/role-transitions", headers=headers)
        assert response.status_code == 403


class TestRolesMetadataVisibility:
    """Locks the public/private boundary between role-graph metadata and per-user assignments."""

    def test_dependencies_anonymous(self, client, admin_headers):
        headers, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "dep_a", "display_name": "Dep A"}, headers=headers).json()
        response = client.get(f"/api/roles/{role['id']}/dependencies")
        assert response.status_code == 200
        assert response.json() == {"items": []}

    def test_dependencies_authenticated_non_admin(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "dep_b", "display_name": "Dep B"}, headers=admin_h).json()
        response = client.get(f"/api/roles/{role['id']}/dependencies", headers=user_h)
        assert response.status_code == 200
        assert response.json() == {"items": []}

    def test_dependencies_unknown_role_anonymous(self, client):
        response = client.get("/api/roles/9999/dependencies")
        assert response.status_code == 404

    def test_conflicts_anonymous(self, client, admin_headers):
        headers, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "conf_a", "display_name": "Conf A"}, headers=headers).json()
        response = client.get(f"/api/roles/{role['id']}/conflicts")
        assert response.status_code == 200
        assert response.json() == {"items": []}

    def test_conflicts_authenticated_non_admin(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = client.post("/api/roles/", json={"name": "conf_b", "display_name": "Conf B"}, headers=admin_h).json()
        response = client.get(f"/api/roles/{role['id']}/conflicts", headers=user_h)
        assert response.status_code == 200
        assert response.json() == {"items": []}

    def test_conflicts_unknown_role_anonymous(self, client):
        response = client.get("/api/roles/9999/conflicts")
        assert response.status_code == 404

    def test_check_conflicts_anonymous(self, client, admin_headers, create_user):
        headers, _ = admin_headers
        role = client.post("/api/roles/", json={"name": "chk_a", "display_name": "Chk A"}, headers=headers).json()
        target, _ = create_user(username="chk_anon", email="chk_anon@test.com")
        response = client.get(f"/api/roles/{role['id']}/check-conflicts?user_id={target.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["conflicts"] == []
        assert data["unfulfilled_dependencies"] == []

    def test_check_conflicts_authenticated_non_admin(self, client, admin_headers, auth_headers):
        admin_h, _ = admin_headers
        user_h, user = auth_headers
        role = client.post("/api/roles/", json={"name": "chk_b", "display_name": "Chk B"}, headers=admin_h).json()
        response = client.get(f"/api/roles/{role['id']}/check-conflicts?user_id={user.id}", headers=user_h)
        assert response.status_code == 200
        data = response.json()
        assert data["conflicts"] == []
        assert data["unfulfilled_dependencies"] == []

    def test_check_conflicts_unknown_role_anonymous(self, client, create_user):
        target, _ = create_user(username="chk_ghost", email="chk_ghost@test.com")
        response = client.get(f"/api/roles/9999/check-conflicts?user_id={target.id}")
        assert response.status_code == 404

    def test_roles_list_still_requires_auth(self, client):
        """GET /api/roles/ enumerates assignments, so it must stay authenticated."""
        response = client.get("/api/roles/")
        assert response.status_code == 401

    def test_role_transitions_list_still_requires_auth(self, client):
        response = client.get("/api/role-transitions/")
        assert response.status_code == 401

    def test_user_role_transitions_still_requires_auth(self, client, create_user):
        target, _ = create_user(username="trans_anon", email="trans_anon@test.com")
        response = client.get(f"/api/users/{target.id}/role-transitions")
        assert response.status_code == 401

    def test_user_roles_list_still_requires_auth(self, client, create_user):
        target, _ = create_user(username="uroles_anon", email="uroles_anon@test.com")
        response = client.get(f"/api/users/{target.id}/roles/")
        assert response.status_code == 401

    def test_user_participant_tags_list_still_requires_auth(self, client, create_user):
        target, _ = create_user(username="utags_anon", email="utags_anon@test.com")
        response = client.get(f"/api/users/{target.id}/participant-tags/")
        assert response.status_code == 401


class TestRoleDependencyAndConflictWrites:
    """Tests for POST/DELETE on /api/role-dependencies/ and /api/role-conflicts/."""

    def _role(self, client, headers, name):
        return client.post("/api/roles/", json={"name": name, "display_name": name}, headers=headers).json()

    def test_create_dependency_success(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "dep_write_role")
        depends_on = self._role(client, headers, "dep_write_parent")
        response = client.post(
            f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}"
            "&dependency_type=required&notes=needs+vip",
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role_id"] == role["id"]
        assert data["depends_on_role_id"] == depends_on["id"]
        assert data["dependency_type"] == "required"
        assert data["notes"] == "needs vip"

    def test_create_dependency_is_listed(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "dep_write_listed")
        depends_on = self._role(client, headers, "dep_write_listed_parent")
        client.post(
            f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}",
            headers=headers,
        )
        response = client.get(f"/api/roles/{role['id']}/dependencies")
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["depends_on_role_id"] == depends_on["id"]

    def test_create_dependency_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = self._role(client, admin_h, "dep_write_forbidden")
        depends_on = self._role(client, admin_h, "dep_write_forbidden_parent")
        response = client.post(
            f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}",
            headers=user_h,
        )
        assert response.status_code == 403

    def test_create_dependency_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "dep_write_noauth")
        depends_on = self._role(client, headers, "dep_write_noauth_parent")
        response = client.post(f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}")
        assert response.status_code == 401

    def test_delete_dependency_success(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "dep_delete_role")
        depends_on = self._role(client, headers, "dep_delete_parent")
        created = client.post(
            f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}",
            headers=headers,
        ).json()
        response = client.delete(f"/api/role-dependencies/{created['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Dependency deleted"
        listed = client.get(f"/api/roles/{role['id']}/dependencies").json()["items"]
        assert listed == []

    def test_delete_dependency_twice_is_404(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "dep_delete_twice")
        depends_on = self._role(client, headers, "dep_delete_twice_parent")
        created = client.post(
            f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}",
            headers=headers,
        ).json()
        assert client.delete(f"/api/role-dependencies/{created['id']}", headers=headers).status_code == 200
        response = client.delete(f"/api/role-dependencies/{created['id']}", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.text.lower()

    def test_delete_dependency_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/role-dependencies/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_dependency_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = self._role(client, admin_h, "dep_delete_forbidden")
        depends_on = self._role(client, admin_h, "dep_delete_forbidden_parent")
        created = client.post(
            f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}",
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/role-dependencies/{created['id']}", headers=user_h)
        assert response.status_code == 403

    def test_delete_dependency_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "dep_delete_noauth")
        depends_on = self._role(client, headers, "dep_delete_noauth_parent")
        created = client.post(
            f"/api/role-dependencies/?role_id={role['id']}&depends_on_role_id={depends_on['id']}",
            headers=headers,
        ).json()
        response = client.delete(f"/api/role-dependencies/{created['id']}")
        assert response.status_code == 401

    def test_create_conflict_success(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "conf_write_role")
        conflicts_with = self._role(client, headers, "conf_write_other")
        response = client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}"
            "&conflict_type=exclusive&notes=mutually+exclusive",
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role_id"] == role["id"]
        assert data["conflicts_with_role_id"] == conflicts_with["id"]
        assert data["conflict_type"] == "exclusive"
        assert data["notes"] == "mutually exclusive"

    def test_create_conflict_is_listed(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "conf_write_listed")
        conflicts_with = self._role(client, headers, "conf_write_listed_other")
        client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}",
            headers=headers,
        )
        response = client.get(f"/api/roles/{role['id']}/conflicts")
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["conflicts_with_role_id"] == conflicts_with["id"]

    def test_create_conflict_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = self._role(client, admin_h, "conf_write_forbidden")
        conflicts_with = self._role(client, admin_h, "conf_write_forbidden_other")
        response = client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}",
            headers=user_h,
        )
        assert response.status_code == 403

    def test_create_conflict_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "conf_write_noauth")
        conflicts_with = self._role(client, headers, "conf_write_noauth_other")
        response = client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}"
        )
        assert response.status_code == 401

    def test_delete_conflict_success(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "conf_delete_role")
        conflicts_with = self._role(client, headers, "conf_delete_other")
        created = client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}",
            headers=headers,
        ).json()
        response = client.delete(f"/api/role-conflicts/{created['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Conflict deleted"
        listed = client.get(f"/api/roles/{role['id']}/conflicts").json()["items"]
        assert listed == []

    def test_delete_conflict_twice_is_404(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "conf_delete_twice")
        conflicts_with = self._role(client, headers, "conf_delete_twice_other")
        created = client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}",
            headers=headers,
        ).json()
        assert client.delete(f"/api/role-conflicts/{created['id']}", headers=headers).status_code == 200
        response = client.delete(f"/api/role-conflicts/{created['id']}", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.text.lower()

    def test_delete_conflict_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/role-conflicts/9999", headers=headers)
        assert response.status_code == 404

    def test_delete_conflict_requires_admin(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        user_h, _ = auth_headers
        role = self._role(client, admin_h, "conf_delete_forbidden")
        conflicts_with = self._role(client, admin_h, "conf_delete_forbidden_other")
        created = client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}",
            headers=admin_h,
        ).json()
        response = client.delete(f"/api/role-conflicts/{created['id']}", headers=user_h)
        assert response.status_code == 403

    def test_delete_conflict_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        role = self._role(client, headers, "conf_delete_noauth")
        conflicts_with = self._role(client, headers, "conf_delete_noauth_other")
        created = client.post(
            f"/api/role-conflicts/?role_id={role['id']}&conflicts_with_role_id={conflicts_with['id']}",
            headers=headers,
        ).json()
        response = client.delete(f"/api/role-conflicts/{created['id']}")
        assert response.status_code == 401
