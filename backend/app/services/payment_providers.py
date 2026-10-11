"""Payment provider abstraction (strategy pattern).

``PAYMENTS_PROVIDER`` selects the implementation: ``mock`` (default),
``stripe`` or ``redsys``. Only ``mock`` works without extra configuration;
the other two fail fast with a clear message until keys/SDK are provided.
"""

import secrets
from abc import ABC, abstractmethod

from app.config import settings
from app.models.payment import Payment


class ProviderNotConfigured(Exception):
    """Raised when a provider is selected but its credentials/SDK are missing."""


class PaymentProvider(ABC):
    """Checkout + confirmation contract every gateway must implement."""

    name: str = ""

    @abstractmethod
    def create_checkout(self, amount: float, currency: str) -> tuple[str, str]:
        """Create a checkout and return ``(provider_ref, checkout_url)``."""

    @abstractmethod
    def confirm(self, payment: Payment) -> str:
        """Return the canonical status: ``paid``, ``failed`` or ``pending``."""


class MockPaymentProvider(PaymentProvider):
    name = "mock"

    def create_checkout(self, amount: float, currency: str) -> tuple[str, str]:
        ref = f"mock_{secrets.token_hex(8)}"
        return ref, f"mock://pay/{ref}"

    def confirm(self, payment: Payment) -> str:
        if (payment.amount or 0) <= 0:
            return "failed"
        if getattr(settings, "MOCK_PAYMENTS_FORCE_FAIL", False):
            return "failed"
        return "paid"


class StripePaymentProvider(PaymentProvider):
    """Stripe Checkout stub (https://docs.stripe.com/checkout).

    Requires ``pip install stripe`` plus ``STRIPE_SECRET_KEY`` (and
    ``STRIPE_WEBHOOK_SECRET`` to verify ``/payments/webhook/stripe``).
    Until then every operation raises :class:`ProviderNotConfigured`.
    """

    name = "stripe"

    def _client(self):
        try:
            import stripe
        except ImportError:
            raise ProviderNotConfigured("Stripe selected but the 'stripe' package is not installed")
        if not settings.STRIPE_SECRET_KEY:
            raise ProviderNotConfigured("Stripe selected but STRIPE_SECRET_KEY is not set")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe

    def create_checkout(self, amount: float, currency: str) -> tuple[str, str]:
        stripe = self._client()
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": currency.lower(),
                        "product_data": {"name": "Clakettes payment"},
                        "unit_amount": int(round(amount * 100)),
                    },
                    "quantity": 1,
                }
            ],
            success_url="{CHECKOUT_SESSION_ID}",
            cancel_url="{CHECKOUT_SESSION_ID}",
        )
        return session.id, session.url

    def confirm(self, payment: Payment) -> str:
        stripe = self._client()
        session = stripe.checkout.Session.retrieve(payment.provider_ref)
        return "paid" if session.payment_status == "paid" else "pending"

    def verify_webhook(self, payload: bytes, signature: str) -> dict | None:
        """Return the Stripe event if ``signature`` is valid, else None."""
        stripe = self._client()
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ProviderNotConfigured("STRIPE_WEBHOOK_SECRET is not set")
        try:
            event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return None
        return {"id": event["id"], "type": event["type"], "object": event["data"]["object"]}


class RedsysPaymentProvider(PaymentProvider):
    """Redsys redirect stub (HMAC_SHA256_V1, no SDK needed).

    Requires ``REDSYS_MERCHANT_CODE`` + ``REDSYS_SECRET_KEY`` (base64 del banco).
    La firma sigue el protocolo del banco; validar contra el sandbox
    (sis-t.redsys.es) antes de producción.
    """

    name = "redsys"
    signature_version = "HMAC_SHA256_V1"

    def _config(self) -> None:
        if not settings.REDSYS_MERCHANT_CODE or not settings.REDSYS_SECRET_KEY:
            raise ProviderNotConfigured("Redsys selected but REDSYS_MERCHANT_CODE / REDSYS_SECRET_KEY are not set")

    @staticmethod
    def _derive_key(secret_b64: str, order: str) -> bytes:
        import base64

        try:
            from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
        except ImportError:
            from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
        from cryptography.hazmat.primitives.ciphers import Cipher, modes

        key = base64.b64decode(secret_b64 + "=" * (-len(secret_b64) % 4))
        cipher = Cipher(TripleDES(key), modes.CBC(b"\0" * 8))
        encryptor = cipher.encryptor()
        padded = order.encode() + b"\0" * ((8 - len(order) % 8) % 8)
        return encryptor.update(padded) + encryptor.finalize()

    @classmethod
    def sign_parameters(cls, secret_b64: str, order: str, params_b64: str) -> str:
        import base64
        import hashlib
        import hmac

        derived = cls._derive_key(secret_b64, order)
        digest = hmac.new(derived, params_b64.encode(), hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    @classmethod
    def encode_parameters(cls, params: dict) -> str:
        import base64
        import json

        return base64.b64encode(json.dumps(params).encode()).decode()

    def create_checkout(self, amount: float, currency: str, pay_methods: str = "C") -> tuple[str, str]:
        """Build a signed Redsys redirect URL.

        ``pay_methods`` selects the rail: ``"C"`` card (default), ``"z"`` Bizum
        (must be enabled on the merchant account — no separate integration).
        """
        import time
        from urllib.parse import quote

        self._config()
        order = time.strftime("%H%M%S") + f"{secrets.randbelow(10**6):06d}"
        params = {
            "DS_MERCHANT_AMOUNT": str(int(round(amount * 100))),
            "DS_MERCHANT_ORDER": order,
            "DS_MERCHANT_MERCHANTCODE": settings.REDSYS_MERCHANT_CODE,
            "DS_MERCHANT_CURRENCY": settings.REDSYS_CURRENCY,
            "DS_MERCHANT_TRANSACTIONTYPE": "0",
            "DS_MERCHANT_TERMINAL": settings.REDSYS_TERMINAL,
            "DS_MERCHANT_MERCHANTURL": "",
            "DS_MERCHANT_PAYMETHODS": pay_methods,
        }
        params_b64 = self.encode_parameters(params)
        signature = self.sign_parameters(settings.REDSYS_SECRET_KEY, order, params_b64)
        host = "sis-t.redsys.es:25443" if settings.REDSYS_SANDBOX else "sis.redsys.es"
        url = f"https://{host}/sis/realizarPago"
        query = (
            f"?Ds_SignatureVersion={self.signature_version}"
            f"&Ds_MerchantParameters={quote(params_b64, safe='')}"
            f"&Ds_Signature={quote(signature, safe='')}"
        )
        return order, url + query

    def confirm(self, payment: Payment) -> str:
        return "pending"

    def verify_response(self, params_b64: str, signature_b64: str, signature_version: str) -> dict | None:
        """Validate a Redsys notification; return payload dict, or None if invalid."""
        import base64
        import json

        self._config()
        if signature_version != self.signature_version:
            return None
        try:
            payload = json.loads(base64.b64decode(params_b64).decode())
        except (ValueError, KeyError):
            return None
        order = str(payload.get("Ds_Order", payload.get("DS_MERCHANT_ORDER", "")))
        if not order:
            return None
        expected = self.sign_parameters(settings.REDSYS_SECRET_KEY, order, params_b64)
        if not secrets.compare_digest(expected, signature_b64.replace("_", "/").replace("-", "+")):
            return None
        return payload

    @staticmethod
    def is_paid(payload: dict) -> bool:
        """Ds_Response 0000-0099 means authorized."""
        try:
            return 0 <= int(str(payload.get("Ds_Response", ""))) <= 99
        except (TypeError, ValueError):
            return False


_PROVIDERS: dict[str, type[PaymentProvider]] = {
    MockPaymentProvider.name: MockPaymentProvider,
    StripePaymentProvider.name: StripePaymentProvider,
    RedsysPaymentProvider.name: RedsysPaymentProvider,
}


def get_provider(name: str | None = None) -> PaymentProvider:
    """Instantiate the configured provider; ValueError on unknown name."""
    selected = (name or settings.PAYMENTS_PROVIDER or "mock").lower()
    cls = _PROVIDERS.get(selected)
    if cls is None:
        raise ValueError(f"Unknown PAYMENTS_PROVIDER '{selected}' (mock|stripe|redsys)")
    return cls()
