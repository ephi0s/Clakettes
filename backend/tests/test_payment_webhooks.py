"""Tests for signed Stripe/Redsys payment webhooks."""

import base64
import os

from app.services.payment_providers import RedsysPaymentProvider, StripePaymentProvider


def _secret() -> str:
    return base64.b64encode(os.urandom(24)).decode()


def _configure_redsys(monkeypatch, secret: str) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "REDSYS_MERCHANT_CODE", "999008881")
    monkeypatch.setattr(settings, "REDSYS_SECRET_KEY", secret)


def _redsys_response(provider, secret: str, order: str, ds_response: str = "0000") -> dict:
    params = {
        "DS_MERCHANT_AMOUNT": "1000",
        "DS_MERCHANT_ORDER": order,
        "DS_MERCHANT_MERCHANTCODE": "999008881",
        "Ds_Response": ds_response,
    }
    params_b64 = provider.encode_parameters(params)
    return {
        "Ds_SignatureVersion": provider.signature_version,
        "Ds_MerchantParameters": params_b64,
        "Ds_Signature": provider.sign_parameters(secret, order, params_b64),
    }


def _paid_payment(db_session, order: str, provider_name: str):
    from app.models.festival import Festival
    from app.models.payment import Payment
    from app.models.registration import FestivalRegistration

    fest = Festival(name="Webhook Fest", is_active=True)
    db_session.add(fest)
    db_session.commit()
    reg = FestivalRegistration(user_id=1, festival_id=fest.id, payment_status="pending")
    db_session.add(reg)
    db_session.commit()
    pay = Payment(
        registration_id=reg.id,
        amount=10.0,
        currency="EUR",
        status="pending",
        provider=provider_name,
        provider_ref=order,
    )
    db_session.add(pay)
    db_session.commit()
    return pay, reg


class TestRedsysWebhook:
    def test_paid_then_idempotent_and_no_revert(self, client, db_session, monkeypatch):
        secret = _secret()
        _configure_redsys(monkeypatch, secret)
        provider = RedsysPaymentProvider()
        order = "123456ABC"
        pay, reg = _paid_payment(db_session, order, "redsys")
        signed = _redsys_response(provider, secret, order)

        first = client.post("/api/payments/webhook/redsys", json=signed)
        assert first.status_code == 200
        assert first.json() == {"received": True, "status": "paid"}
        db_session.refresh(pay)
        db_session.refresh(reg)
        assert pay.status == "paid"
        assert reg.payment_status == "paid"
        assert reg.transaction_id == order
        paid_at = reg.paid_at

        repeated = client.post("/api/payments/webhook/redsys", json=signed)
        assert repeated.status_code == 200
        assert repeated.json()["status"] == "paid"
        db_session.refresh(reg)
        assert reg.paid_at == paid_at

        unpaid = _redsys_response(provider, secret, order, ds_response="0101")
        late = client.post("/api/payments/webhook/redsys", json=unpaid)
        assert late.status_code == 200
        assert late.json()["status"] == "paid"
        db_session.refresh(pay)
        db_session.refresh(reg)
        assert pay.status == "paid"
        assert reg.payment_status == "paid"

    def test_form_encoded_body(self, client, db_session, monkeypatch):
        secret = _secret()
        _configure_redsys(monkeypatch, secret)
        provider = RedsysPaymentProvider()
        order = "FORM123"
        pay, _ = _paid_payment(db_session, order, "redsys")
        signed = _redsys_response(provider, secret, order)
        response = client.post("/api/payments/webhook/redsys", data=signed)
        assert response.status_code == 200
        assert response.json()["status"] == "paid"
        db_session.refresh(pay)
        assert pay.status == "paid"

    def test_invalid_signature(self, client, db_session, monkeypatch):
        secret = _secret()
        _configure_redsys(monkeypatch, secret)
        provider = RedsysPaymentProvider()
        order = "BADSIG"
        pay, reg = _paid_payment(db_session, order, "redsys")
        signed = _redsys_response(provider, secret, order)
        signed["Ds_Signature"] = "tampered"
        response = client.post("/api/payments/webhook/redsys", json=signed)
        assert response.status_code == 400
        db_session.refresh(pay)
        db_session.refresh(reg)
        assert pay.status == "pending"
        assert reg.payment_status == "pending"

    def test_not_configured(self, client, db_session, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "REDSYS_MERCHANT_CODE", "")
        monkeypatch.setattr(settings, "REDSYS_SECRET_KEY", "")
        response = client.post("/api/payments/webhook/redsys", json={})
        assert response.status_code == 502


class TestStripeWebhook:
    def _patch_verify(self, monkeypatch):
        def fake(self, payload, signature):
            if signature != "valid":
                return None
            return {
                "id": "evt_1",
                "type": "checkout.session.completed",
                "object": {"id": "cs_test_123", "payment_status": "paid"},
            }

        monkeypatch.setattr(StripePaymentProvider, "verify_webhook", fake)

    def test_paid_then_idempotent(self, client, db_session, monkeypatch):
        self._patch_verify(monkeypatch)
        pay, reg = _paid_payment(db_session, "cs_test_123", "stripe")

        first = client.post("/api/payments/webhook/stripe", json={}, headers={"stripe-signature": "valid"})
        assert first.status_code == 200
        assert first.json() == {"received": True, "status": "paid"}
        db_session.refresh(pay)
        db_session.refresh(reg)
        assert pay.status == "paid"
        assert reg.payment_status == "paid"
        paid_at = reg.paid_at

        repeated = client.post("/api/payments/webhook/stripe", json={}, headers={"stripe-signature": "valid"})
        assert repeated.status_code == 200
        assert repeated.json()["status"] == "paid"
        db_session.refresh(reg)
        assert reg.paid_at == paid_at

    def test_invalid_signature(self, client, db_session, monkeypatch):
        self._patch_verify(monkeypatch)
        pay, reg = _paid_payment(db_session, "cs_test_123", "stripe")
        response = client.post("/api/payments/webhook/stripe", json={}, headers={"stripe-signature": "bad"})
        assert response.status_code == 400
        db_session.refresh(pay)
        db_session.refresh(reg)
        assert pay.status == "pending"
        assert reg.payment_status == "pending"

    def test_not_configured(self, client, db_session, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "")
        monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        response = client.post("/api/payments/webhook/stripe", json={})
        assert response.status_code == 502
