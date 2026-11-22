from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.routers.permissions import is_admin, require_festival_admin
from app.routers.dependencies import get_or_404
from app.models.payment import Payment
from app.schemas.payment import PaymentCheckoutRequest, PaymentPage, PaymentResponse, WebhookResponse
from app.services.payment_providers import (
    PaymentConfirmationError,
    ProviderNotConfigured,
    RedsysPaymentProvider,
    StripePaymentProvider,
)
from app.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()


def _manages_festival(db: Session, user: User, festival_id: int) -> bool:
    try:
        require_festival_admin(db, user, festival_id)
        return True
    except HTTPException:
        return False


def _require_payment_access(db: Session, current_user: User, obj) -> None:
    """Owner (via registration), festival admin or global admin only."""
    from app.models.event import Event
    from app.models.registration import FestivalRegistration

    if is_admin(current_user):
        return
    if obj.registration_id is not None:
        reg = db.query(FestivalRegistration).filter(FestivalRegistration.id == obj.registration_id).first()
        if reg and (reg.user_id == current_user.id or _manages_festival(db, current_user, reg.festival_id)):
            return
    elif obj.event_id is not None:
        event = db.query(Event).filter(Event.id == obj.event_id).first()
        if event and _manages_festival(db, current_user, event.festival_id):
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


@router.post("/payments/checkout", response_model=PaymentResponse, status_code=201)
async def checkout(
    body: PaymentCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.registration_id is None and body.event_id is None:
        raise HTTPException(status_code=422, detail="registration_id or event_id required")
    return payment_service.create_checkout(db, body)


@router.get("/payments/", response_model=PaymentPage)
async def list_payments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(payment_service.model)
    if status:
        q = q.filter(payment_service.model.status == status)
    if not is_admin(current_user):
        from app.models.registration import FestivalRegistration

        reg_ids = [
            r.id for r in db.query(FestivalRegistration).filter(FestivalRegistration.user_id == current_user.id).all()
        ]
        q = q.filter(payment_service.model.registration_id.in_(reg_ids)) if reg_ids else q.filter(False)
    return payment_service.paginate(q.order_by(payment_service.model.id.desc()), page, size)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_or_404(db, Payment, payment_id, "Payment")
    _require_payment_access(db, current_user, obj)
    return obj


@router.post("/payments/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: int,
    body: dict | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = get_or_404(db, Payment, payment_id, "Payment")
    _require_payment_access(db, current_user, obj)
    try:
        return payment_service.confirm(db, obj, response=body)
    except PaymentConfirmationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/payments/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    obj = get_or_404(db, Payment, payment_id, "Payment")
    if obj.registration_id is not None:
        from app.models.registration import FestivalRegistration

        reg = db.query(FestivalRegistration).filter(FestivalRegistration.id == obj.registration_id).first()
        if reg:
            require_festival_admin(db, current_user, reg.festival_id)
    elif not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return payment_service.refund(db, obj)


@router.post("/payments/webhook/mock", response_model=PaymentResponse)
async def mock_webhook(body: dict, request: Request, db: Session = Depends(get_db)):
    """Simulated provider callback — requires the shared webhook secret."""
    from app.config import settings

    expected = settings.MOCK_WEBHOOK_SECRET
    provided = request.headers.get("x-webhook-secret", "")
    if not expected or provided != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook secret")
    ref = body.get("provider_ref")
    pay_status = body.get("status", "paid")
    if not ref:
        raise HTTPException(status_code=422, detail="provider_ref required")
    obj = db.query(payment_service.model).filter(payment_service.model.provider_ref == ref).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    if pay_status == "paid":
        return payment_service.confirm(db, obj)
    obj.status = "failed"
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/payments/webhook/stripe", response_model=WebhookResponse)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    stripe = StripePaymentProvider()
    try:
        event = stripe.verify_webhook(payload, signature)
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    if event is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe webhook signature")
    obj = event.get("object") or {}
    ref = str(obj.get("id") or "")
    payment = (
        db.query(Payment).filter(Payment.provider == "stripe", Payment.provider_ref == ref).first() if ref else None
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    new_status = "paid" if obj.get("payment_status") == "paid" else "pending"
    payment = payment_service.apply_webhook_status(db, payment, new_status)
    return WebhookResponse(received=True, status=payment.status)


@router.post("/payments/webhook/redsys", response_model=WebhookResponse)
async def redsys_webhook(request: Request, db: Session = Depends(get_db)):
    form = dict(await request.form())
    if not form:
        try:
            form = await request.json()
        except ValueError:
            form = {}
    params_b64 = str(form.get("Ds_MerchantParameters") or form.get("ds_merchant_parameters") or "")
    signature_b64 = str(form.get("Ds_Signature") or form.get("ds_signature") or "")
    signature_version = str(form.get("Ds_SignatureVersion") or form.get("ds_signature_version") or "")
    redsys = RedsysPaymentProvider()
    try:
        payload = redsys.verify_response(params_b64, signature_b64, signature_version)
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Redsys webhook signature")
    order = str(payload.get("Ds_Order") or payload.get("DS_MERCHANT_ORDER") or "")
    payment = (
        db.query(Payment).filter(Payment.provider == "redsys", Payment.provider_ref == order).first() if order else None
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    new_status = "paid" if redsys.is_paid(payload) else "pending"
    payment = payment_service.apply_webhook_status(db, payment, new_status)
    return WebhookResponse(received=True, status=payment.status)
