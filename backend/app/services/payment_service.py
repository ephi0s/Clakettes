from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.schemas.payment import PaymentCheckoutRequest
from app.services.payment_providers import get_provider
from .base_service import BaseService


class PaymentService(BaseService[Payment, PaymentCheckoutRequest, PaymentCheckoutRequest]):
    def __init__(self, provider=None):
        super().__init__(Payment)
        self.provider = provider or get_provider()

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
            provider=self.provider.name,
            status="pending",
            provider_ref=ref,
            checkout_url=url,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def _sync_registration(self, db: Session, payment: Payment, status: str) -> None:
        if payment.registration_id is None:
            return
        from app.models.registration import FestivalRegistration

        reg = db.query(FestivalRegistration).filter(FestivalRegistration.id == payment.registration_id).first()
        if not reg:
            return
        reg.payment_status = status
        if status == "paid":
            from datetime import datetime, timezone

            reg.paid_at = datetime.now(timezone.utc)
            reg.payment_method = payment.provider
            reg.transaction_id = payment.provider_ref

    def confirm(self, db: Session, payment: Payment, response: dict | None = None) -> Payment:
        payment.status = self.provider.confirm(payment, response=response)
        if payment.status == "paid":
            self._sync_registration(db, payment, "paid")
        db.commit()
        db.refresh(payment)
        return payment

    def apply_webhook_status(self, db: Session, payment: Payment, status: str) -> Payment:
        if status == "paid":
            if payment.status in ("paid", "refunded"):
                return payment
            payment.status = "paid"
            self._sync_registration(db, payment, "paid")
        elif payment.status not in (None, "", "pending"):
            return payment
        else:
            payment.status = status
        db.commit()
        db.refresh(payment)
        return payment

    def refund(self, db: Session, payment: Payment) -> Payment:
        payment.status = "refunded"
        self._sync_registration(db, payment, "refunded")
        db.commit()
        db.refresh(payment)
        return payment
