from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.routers.permissions import is_admin, require_festival_admin
from app.schemas.payment import PaymentCheckoutRequest, PaymentPage, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()


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
    obj = payment_service.get(db, payment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    return obj


@router.post("/payments/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    obj = payment_service.get(db, payment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment_service.confirm(db, obj)


@router.post("/payments/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    obj = payment_service.get(db, payment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    if obj.registration_id is not None:
        from app.models.registration import FestivalRegistration

        reg = db.query(FestivalRegistration).filter(FestivalRegistration.id == obj.registration_id).first()
        if reg:
            require_festival_admin(db, current_user, reg.festival_id)
    elif not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return payment_service.refund(db, obj)


@router.post("/payments/webhook/mock", response_model=PaymentResponse)
async def mock_webhook(body: dict, db: Session = Depends(get_db)):
    ref = body.get("provider_ref")
    status = body.get("status", "paid")
    if not ref:
        raise HTTPException(status_code=422, detail="provider_ref required")
    obj = db.query(payment_service.model).filter(payment_service.model.provider_ref == ref).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    if status == "paid":
        return payment_service.confirm(db, obj)
    obj.status = "failed"
    db.commit()
    db.refresh(obj)
    return obj
