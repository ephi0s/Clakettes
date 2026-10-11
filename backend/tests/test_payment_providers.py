"""Tests for payment provider selection and stubs (mock/stripe/redsys)."""

import pytest

from app.services.payment_providers import (
    MockPaymentProvider,
    ProviderNotConfigured,
    RedsysPaymentProvider,
    StripePaymentProvider,
    get_provider,
)


class TestFactory:
    def test_default_is_mock(self):
        assert isinstance(get_provider(), MockPaymentProvider)

    def test_unknown_name_rejected(self):
        with pytest.raises(ValueError, match="Unknown PAYMENTS_PROVIDER"):
            get_provider("paypal")

    def test_mock_flow(self, db_session):
        from app.models.payment import Payment
        from app.services.payment_service import PaymentService

        svc = PaymentService(provider=MockPaymentProvider())
        pay = Payment(amount=10.0, currency="EUR", status="pending", provider_ref="x")
        assert svc.provider.confirm(pay) == "paid"
        pay.amount = 0
        assert svc.provider.confirm(pay) == "failed"


class TestStripeStub:
    def test_missing_sdk_or_key_fails_fast(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "")
        provider = StripePaymentProvider()
        with pytest.raises(ProviderNotConfigured):
            provider.create_checkout(10.0, "EUR")


class TestRedsysStub:
    @staticmethod
    def _key() -> str:
        import base64
        import os

        return base64.b64encode(os.urandom(24)).decode()

    def test_missing_config_fails_fast(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "REDSYS_MERCHANT_CODE", "")
        monkeypatch.setattr(settings, "REDSYS_SECRET_KEY", "")
        with pytest.raises(ProviderNotConfigured):
            RedsysPaymentProvider().create_checkout(10.0, "EUR")

    def test_sign_verify_roundtrip(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "REDSYS_MERCHANT_CODE", "999008881")
        monkeypatch.setattr(settings, "REDSYS_SECRET_KEY", self._key())
        provider = RedsysPaymentProvider()
        order, url = provider.create_checkout(10.0, "EUR")
        assert url.startswith("https://sis-t.redsys.es:25443/sis/realizarPago")
        import base64
        import json
        from urllib.parse import parse_qs, urlparse

        query = parse_qs(urlparse(url).query)
        params_b64 = query["Ds_MerchantParameters"][0]
        assert json.loads(base64.b64decode(params_b64))["DS_MERCHANT_PAYMETHODS"] == "C"
        _, bizum_url = provider.create_checkout(10.0, "EUR", pay_methods="z")
        bizum_params = parse_qs(urlparse(bizum_url).query)["Ds_MerchantParameters"][0]
        assert json.loads(base64.b64decode(bizum_params))["DS_MERCHANT_PAYMETHODS"] == "z"
        provider2 = RedsysPaymentProvider()
        verified = provider2.verify_response(params_b64, query["Ds_Signature"][0], query["Ds_SignatureVersion"][0])
        assert verified is not None
        assert verified["DS_MERCHANT_ORDER"] == order
        tampered = base64.b64encode(
            json.dumps({**json.loads(base64.b64decode(params_b64)), "DS_MERCHANT_AMOUNT": "1"}).encode()
        ).decode()
        assert provider2.verify_response(tampered, query["Ds_Signature"][0], "HMAC_SHA256_V1") is None
        assert provider2.verify_response(params_b64, query["Ds_Signature"][0], "OTHER") is None

    def test_is_paid(self):
        assert RedsysPaymentProvider.is_paid({"Ds_Response": "0000"}) is True
        assert RedsysPaymentProvider.is_paid({"Ds_Response": "0099"}) is True
        assert RedsysPaymentProvider.is_paid({"Ds_Response": "0101"}) is False
        assert RedsysPaymentProvider.is_paid({}) is False
