"""Contract tests: authz fixes and frontend-aligned routes."""

from app.models.festival import Festival
from app.models.payment import Payment
from app.models.registration import FestivalRegistration
from app.models.user_festival import user_festival


def _festival(db_session, name="Contract Fest"):
    fest = Festival(name=name, is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    return fest


class TestPaymentsAuthz:
    def _payment(self, db_session, ref="webhook-ref-1"):
        obj = Payment(registration_id=None, event_id=None, amount=10.0, status="pending", provider_ref=ref)
        db_session.add(obj)
        db_session.commit()
        return obj

    def test_webhook_requires_secret(self, client, db_session, monkeypatch):
        from app.config import settings

        self._payment(db_session)
        monkeypatch.setattr(settings, "MOCK_WEBHOOK_SECRET", "s3cret")
        denied = client.post("/api/payments/webhook/mock", json={"provider_ref": "webhook-ref-1"})
        assert denied.status_code == 403
        ok = client.post(
            "/api/payments/webhook/mock",
            json={"provider_ref": "webhook-ref-1"},
            headers={"x-webhook-secret": "s3cret"},
        )
        assert ok.status_code == 200
        assert ok.json()["status"] == "paid"

    def test_payment_detail_requires_owner_or_admin(self, client, auth_headers, create_user, db_session):
        headers, user = auth_headers
        other, _ = create_user(username="other", email="other@example.com")
        fest = _festival(db_session)
        reg = FestivalRegistration(user_id=other.id, festival_id=fest.id)
        db_session.add(reg)
        db_session.commit()
        pay = Payment(registration_id=reg.id, amount=5.0, status="pending", provider_ref="ref-x1")
        db_session.add(pay)
        db_session.commit()
        assert client.get(f"/api/payments/{pay.id}", headers=headers).status_code == 403
        assert client.post(f"/api/payments/{pay.id}/confirm", headers=headers).status_code == 403


class TestRolesHierarchy:
    def test_hierarchy_reachable(self, client):
        response = client.get("/api/roles/hierarchy/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestFestivalCreatorIsOrganizer:
    def test_creator_can_manage_festival(self, client, auth_headers, db_session):
        headers, user = auth_headers
        fest_id = client.post("/api/festivals/", json={"name": "Mine"}, headers=headers).json()["id"]
        row = db_session.execute(
            user_festival.select().where(user_festival.c.user_id == user.id, user_festival.c.festival_id == fest_id)
        ).first()
        assert row is not None and row.role == "organizer"
        updated = client.put(f"/api/festivals/{fest_id}", json={"description": "d"}, headers=headers)
        assert updated.status_code == 200


class TestRegistrationFormShorthands:
    def _form(self, client, headers, db_session):
        fest = _festival(db_session)
        resp = client.post(
            f"/api/festivals/{fest.id}/registration-forms/",
            json={"title": "F", "sections": [{"title": "S1"}]},
            headers=headers,
        )
        assert resp.status_code == 201, resp.text
        return fest, resp.json()

    def test_create_with_sections_in_body(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest, data = self._form(client, headers, db_session)
        assert data["festival_id"] == fest.id
        fetched = client.get(f"/api/registration-forms/{data['id']}", headers=headers).json()
        assert len(fetched["sections"]) == 1
        assert fetched["sections"][0]["title"] == "S1"

    def test_crud_by_id(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest, data = self._form(client, headers, db_session)
        fid = data["id"]
        assert client.get(f"/api/registration-forms/{fid}", headers=headers).status_code == 200
        assert client.put(f"/api/registration-forms/{fid}", json={"title": "F2"}, headers=headers).status_code == 200
        assert client.delete(f"/api/registration-forms/{fid}", headers=headers).status_code == 200

    def test_links_lifecycle_by_id(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        _, data = self._form(client, headers, db_session)
        fid = data["id"]
        created = client.post(f"/api/registration-forms/{fid}/links/", json={}, headers=headers)
        assert created.status_code == 201, created.text
        link_id = created.json()["id"]
        listed = client.get(f"/api/registration-forms/{fid}/links/", headers=headers)
        assert listed.json()["total"] == 1
        regen = client.post(f"/api/registration-form-links/{link_id}/regenerate", headers=headers)
        assert regen.status_code == 200
        assert regen.json()["token"] != created.json()["token"]
        assert client.delete(f"/api/registration-form-links/{link_id}", headers=headers).status_code == 200

    def test_registrations_by_form(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest, data = self._form(client, headers, db_session)
        reg = FestivalRegistration(user_id=1, festival_id=fest.id, form_id=data["id"])
        db_session.add(reg)
        db_session.commit()
        listed = client.get(f"/api/registration-forms/{data['id']}/registrations/", headers=headers)
        assert listed.status_code == 200
        assert listed.json()["total"] == 1
