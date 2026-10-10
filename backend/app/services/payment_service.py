import secrets
from sqlalchemy.orm import Session
from app.config import settings
from app.models.payment import Payment
from app.schemas.payment import PaymentCheckoutRequest
from .base_service import BaseService


class MockPaymentProvider:
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


class PaymentService(BaseService[Payment, PaymentCheckoutRequest, PaymentCheckoutRequest]):
    def __init__(self):
        super().__init__(Payment)
        self.provider = MockPaymentProvider()

    def create_checkout(self, db: Session, data: PaymentCheckoutRequest) -> Payment:
        amount = data.amount
        if amount is None and data.registration_id is not None:
            from app.models.registration import FestivalRegistration

            reg = db.query(FestivalRegistration).filter(FestivalRegistration.id == data.registration_id).first()
            if reg and reg.form and getattr(reg.form, "fee_amount", None):
                amount = reg.form.fee_amount
        amount = amount if amount is not None else 0.0
        ref, url = self.provider.create_checkout(amount, data.currency)
        obj = Payment(
            registration_id=data.registration_id,
            event_id=data.event_id,
            amount=amount,
            currency=data.currency,
            provider=getattr(settings, "PAYMENTS_PROVIDER", "mock"),
            status="pending",
            provider_ref=ref,
            checkout_url=url,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def confirm(self, db: Session, payment: Payment) -> Payment:
        payment.status = self.provider.confirm(payment)
        if payment.status == "paid" and payment.registration_id is not None:
            from datetime import datetime, timezone
            from app.models.registration import FestivalRegistration

            reg = db.query(FestivalRegistration).filter(FestivalRegistration.id == payment.registration_id).first()
            if reg:
                reg.payment_status = "paid"
                reg.paid_at = datetime.now(timezone.utc)
                reg.payment_method = payment.provider
                reg.transaction_id = payment.provider_ref
        db.commit()
        db.refresh(payment)
        return payment

    def refund(self, db: Session, payment: Payment) -> Payment:
        payment.status = "refunded"
        if payment.registration_id is not None:
            from app.models.registration import FestivalRegistration

            reg = db.query(FestivalRegistration).filter(FestivalRegistration.id == payment.registration_id).first()
            if reg:
                reg.payment_status = "refunded"
        db.commit()
        db.refresh(payment)
        return payment
