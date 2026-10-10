"""Tests for manual/offline registration payments (fee + payment status)."""

from app.auth import create_session
from app.enums import PaymentStatus
from app.models.festival import Festival
from app.models.registration import FestivalRegistration, RegistrationForm, RegistrationFormLink
from app.schemas.user import UserCreate
from app.services.user_service import UserService


def _setup_festival(db_session, name="Fest"):
    fest = Festival(name=name, is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    return fest


def _setup_form(db_session, fest, fee_amount=None, currency="EUR", title="Form"):
    form = RegistrationForm(
        festival_id=fest.id,
        title=title,
        is_active=True,
        fee_amount=fee_amount,
        currency=currency,
    )
    db_session.add(form)
    db_session.commit()
    db_session.refresh(form)
    return form


def _setup_link(db_session, form, token):
    link = RegistrationFormLink(form_id=form.id, token=token, is_active=True)
    db_session.add(link)
    db_session.commit()
    return link


def _register(client, headers, form, token):
    return client.post(
        f"/api/public/forms/{token}/register",
        json={"form_id": form.id, "link_token": token, "sections": []},
        headers=headers,
    )


def _applicant_headers(db_session):
    svc = UserService()
    applicant = svc.create(
        db_session,
        UserCreate(
            username="applicant",
            email="applicant@test.com",
            full_name="Applicant",
            role="user",
            password="Test1234",
        ),
    )
    sess, access_token, _ = create_session(db_session, applicant.id)
    return {"Authorization": f"Bearer {access_token}"}, applicant


class TestRegistrationPaymentStatus:
    """Registering should set payment_status based on the form fee."""

    def test_register_without_fee_is_paid(self, client, auth_headers, db_session):
        headers, user = auth_headers
        fest = _setup_festival(db_session)
        form = _setup_form(db_session, fest)
        _setup_link(db_session, form, "nofee")
        response = _register(client, headers, form, "nofee")
        assert response.status_code == 200
        data = response.json()
        assert data["payment_status"] == PaymentStatus.PAID.value
        assert data["paid_at"] is None

    def test_register_with_fee_is_pending(self, client, auth_headers, db_session):
        headers, user = auth_headers
        fest = _setup_festival(db_session)
        form = _setup_form(db_session, fest, fee_amount=50.0)
        _setup_link(db_session, form, "withfee")
        response = _register(client, headers, form, "withfee")
        assert response.status_code == 200
        data = response.json()
        assert data["payment_status"] == PaymentStatus.PENDING.value
        assert data["form"]["fee_amount"] == 50.0
        assert data["form"]["currency"] == "EUR"


class TestApproveRequiresPayment:
    """Approval must be blocked until the registration is paid."""

    def test_approve_pending_payment_returns_409(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = _setup_festival(db_session)
        form = _setup_form(db_session, fest, fee_amount=50.0)
        _setup_link(db_session, form, "pendingfee")
        applicant_headers, _ = _applicant_headers(db_session)
        response = _register(client, applicant_headers, form, "pendingfee")
        assert response.status_code == 200
        reg_id = response.json()["id"]
        approve_resp = client.post(f"/api/registrations/{reg_id}/approve", headers=headers)
        assert approve_resp.status_code == 409


class TestMarkPaid:
    """POST /api/registrations/{registration_id}/payment/mark-paid"""

    def test_mark_paid_then_approve(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = _setup_festival(db_session)
        form = _setup_form(db_session, fest, fee_amount=50.0)
        _setup_link(db_session, form, "payme")
        applicant_headers, _ = _applicant_headers(db_session)
        response = _register(client, applicant_headers, form, "payme")
        assert response.status_code == 200
        reg_id = response.json()["id"]

        pay_resp = client.post(
            f"/api/registrations/{reg_id}/payment/mark-paid",
            json={"method": "cash", "transaction_id": "TXN-42"},
            headers=headers,
        )
        assert pay_resp.status_code == 200
        data = pay_resp.json()
        assert data["payment_status"] == PaymentStatus.PAID.value
        assert data["paid_at"] is not None
        assert data["payment_method"] == "cash"
        assert data["transaction_id"] == "TXN-42"

        approve_resp = client.post(f"/api/registrations/{reg_id}/approve", headers=headers)
        assert approve_resp.status_code == 200
        assert approve_resp.json()["status"] == "approved"

    def test_mark_paid_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post("/api/registrations/9999/payment/mark-paid", json={}, headers=headers)
        assert response.status_code == 404


class TestMarkRefunded:
    """POST /api/registrations/{registration_id}/payment/mark-refunded"""

    def test_mark_refunded(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        fest = _setup_festival(db_session)
        form = _setup_form(db_session, fest, fee_amount=50.0)
        _setup_link(db_session, form, "refundme")
        applicant_headers, _ = _applicant_headers(db_session)
        response = _register(client, applicant_headers, form, "refundme")
        assert response.status_code == 200
        reg_id = response.json()["id"]

        refund_resp = client.post(f"/api/registrations/{reg_id}/payment/mark-refunded", headers=headers)
        assert refund_resp.status_code == 200
        assert refund_resp.json()["payment_status"] == PaymentStatus.REFUNDED.value

    def test_mark_refunded_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post("/api/registrations/9999/payment/mark-refunded", headers=headers)
        assert response.status_code == 404


class TestPaymentAuthorization:
    """Payment endpoints require a festival admin."""

    def test_payment_endpoints_require_auth(self, client, db_session):
        fest = _setup_festival(db_session)
        reg = FestivalRegistration(user_id=1, festival_id=fest.id)
        db_session.add(reg)
        db_session.commit()
        response = client.post(f"/api/registrations/{reg.id}/payment/mark-paid", json={})
        assert response.status_code == 401
        response = client.post(f"/api/registrations/{reg.id}/payment/mark-refunded")
        assert response.status_code == 401

    def test_payment_endpoints_require_festival_admin(self, client, auth_headers, db_session):
        headers, user = auth_headers
        fest = _setup_festival(db_session)
        _, other = _applicant_headers(db_session)
        reg = FestivalRegistration(user_id=other.id, festival_id=fest.id)
        db_session.add(reg)
        db_session.commit()
        response = client.post(f"/api/registrations/{reg.id}/payment/mark-paid", json={}, headers=headers)
        assert response.status_code == 403
        response = client.post(f"/api/registrations/{reg.id}/payment/mark-refunded", headers=headers)
        assert response.status_code == 403
