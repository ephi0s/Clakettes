"""Tests for festival rulebooks (bases) endpoints."""


def _create_festival(client, headers, name="Fest"):
    resp = client.post("/api/festivals/", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


class TestListRulebooks:
    def test_list_empty(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        resp = client.get(f"/api/festivals/{fest_id}/rulebooks/")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_list_not_found(self, client):
        resp = client.get("/api/festivals/9999/rulebooks/")
        assert resp.status_code == 404


class TestCreateRulebook:
    def test_create_with_external_url(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        resp = client.post(
            f"/api/festivals/{fest_id}/rulebooks/",
            json={
                "title": "Bases oficiales",
                "category": "official_section",
                "external_url": "https://example.com/b.pdf",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "Bases oficiales"

    def test_create_requires_document(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        resp = client.post(
            f"/api/festivals/{fest_id}/rulebooks/",
            json={"title": "Sin doc", "category": "contest"},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_create_invalid_category(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        resp = client.post(
            f"/api/festivals/{fest_id}/rulebooks/",
            json={"title": "X", "category": "nope", "external_url": "https://example.com/b.pdf"},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_create_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        resp = client.post(
            f"/api/festivals/{fest_id}/rulebooks/",
            json={"title": "X", "external_url": "https://example.com/b.pdf"},
        )
        assert resp.status_code == 401

    def test_create_forbidden_for_regular_user(self, client, auth_headers, admin_headers):
        admin, _ = admin_headers
        fest_id = _create_festival(client, admin)
        user_headers, _ = auth_headers
        resp = client.post(
            f"/api/festivals/{fest_id}/rulebooks/",
            json={"title": "X", "external_url": "https://example.com/b.pdf"},
            headers=user_headers,
        )
        assert resp.status_code == 403

    def test_upload_pdf(self, client, admin_headers, tmp_path):
        from pypdf import PdfWriter

        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        pdf = tmp_path / "bases.pdf"
        writer = PdfWriter()
        writer.add_blank_page(100, 100)
        writer.add_metadata({"/Author": "John Doe"})
        with open(pdf, "wb") as f:
            writer.write(f)
        with open(pdf, "rb") as f:
            resp = client.post(
                f"/api/festivals/{fest_id}/rulebooks/upload",
                files={"file": ("bases.pdf", f, "application/pdf")},
                data={"title": "Bases PDF", "category": "contest"},
                headers=headers,
            )
        assert resp.status_code == 201
        assert resp.json()["file_url"].startswith("/uploads/rulebooks/")

    def test_upload_pdf_metadata_stripped(self, client, admin_headers, tmp_path, monkeypatch):
        from pypdf import PdfReader, PdfWriter

        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        monkeypatch.chdir(tmp_path)
        pdf = tmp_path / "meta.pdf"
        writer = PdfWriter()
        writer.add_blank_page(100, 100)
        writer.add_metadata({"/Author": "John Doe"})
        with open(pdf, "wb") as f:
            writer.write(f)
        with open(pdf, "rb") as f:
            resp = client.post(
                f"/api/festivals/{fest_id}/rulebooks/upload",
                files={"file": ("meta.pdf", f, "application/pdf")},
                data={"title": "Meta PDF", "category": "contest"},
                headers=headers,
            )
        assert resp.status_code == 201
        stored = tmp_path / "uploads" / resp.json()["file_url"].split("/uploads/")[1]
        assert PdfReader(str(stored)).metadata.author in (None, "")

    def test_upload_rejects_non_pdf(self, client, admin_headers, tmp_path):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        img = tmp_path / "x.png"
        img.write_bytes(b"not an image")
        with open(img, "rb") as f:
            resp = client.post(
                f"/api/festivals/{fest_id}/rulebooks/upload",
                files={"file": ("x.png", f, "image/png")},
                data={"title": "Bad", "category": "contest"},
                headers=headers,
            )
        assert resp.status_code == 400


class TestUpdateDeleteRulebook:
    def _create(self, client, headers, fest_id):
        resp = client.post(
            f"/api/festivals/{fest_id}/rulebooks/",
            json={"title": "Bases", "category": "activity", "external_url": "https://example.com/b.pdf"},
            headers=headers,
        )
        return resp.json()["id"]

    def test_update(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        rid = self._create(client, headers, fest_id)
        resp = client.put(
            f"/api/festivals/{fest_id}/rulebooks/{rid}",
            json={"title": "Bases v2"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Bases v2"

    def test_update_forbidden_for_regular_user(self, client, auth_headers, admin_headers):
        admin, _ = admin_headers
        fest_id = _create_festival(client, admin)
        rid = self._create(client, admin, fest_id)
        user_headers, _ = auth_headers
        resp = client.put(
            f"/api/festivals/{fest_id}/rulebooks/{rid}",
            json={"title": "Hacked"},
            headers=user_headers,
        )
        assert resp.status_code == 403

    def test_delete(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        rid = self._create(client, headers, fest_id)
        resp = client.delete(f"/api/festivals/{fest_id}/rulebooks/{rid}", headers=headers)
        assert resp.status_code == 200
        get_resp = client.get(f"/api/festivals/{fest_id}/rulebooks/{rid}")
        assert get_resp.status_code == 404

    def test_get_public_without_auth(self, client, admin_headers):
        headers, _ = admin_headers
        fest_id = _create_festival(client, headers)
        rid = self._create(client, headers, fest_id)
        resp = client.get(f"/api/festivals/{fest_id}/rulebooks/{rid}")
        assert resp.status_code == 200
