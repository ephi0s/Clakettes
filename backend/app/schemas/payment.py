from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .common import PageBase


class PaymentCheckoutRequest(BaseModel):
    registration_id: int | None = None
    event_id: int | None = None
    amount: float | None = None
    currency: str = "EUR"


class PaymentResponse(BaseModel):
    id: int
    registration_id: int | None = None
    event_id: int | None = None
    amount: float
    currency: str
    provider: str
    status: str
    provider_ref: str | None = None
    checkout_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentPage(PageBase):
    items: list[PaymentResponse]
