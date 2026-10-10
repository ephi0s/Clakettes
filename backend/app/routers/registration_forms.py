"""Router for registration forms, links, sections, and festival registrations."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.registration import (
    RegistrationFormCreate,
    RegistrationFormUpdate,
    RegistrationFormResponse,
    RegistrationFormPublicResponse,
    RegistrationFormSectionCreate,
    RegistrationFormSectionUpdate,
    RegistrationFormSectionResponse,
    RegistrationFormLinkCreate,
    RegistrationFormLinkResponse,
    RegistrationFormLinkPage,
    RegistrationFormPage,
    FestivalRegistrationCreate,
    FestivalRegistrationUpdate,
    FestivalRegistrationResponse,
    FestivalRegistrationPage,
    PaymentUpdate,
)
from app.services.registration_service import (
    RegistrationFormService,
    RegistrationFormSectionService,
    RegistrationFormLinkService,
    FestivalRegistrationService,
)
from app.services.festival_service import FestivalService
from app.services.user_service import UserService
from app.services.export_service import export_registrations_csv, export_registrations_pdf
from app.routers.permissions import is_admin, require_festival_admin
from app.routers.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()

form_service = RegistrationFormService()
section_service = RegistrationFormSectionService()
link_service = RegistrationFormLinkService()
reg_service = FestivalRegistrationService()
festival_service = FestivalService()
user_service = UserService()


@router.get("/festivals/{festival_id}/registration-forms/", response_model=RegistrationFormPage)
async def list_registration_forms(
    festival_id: int,
    is_active: bool | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    return form_service.get_by_festival_paginated(db, festival_id, page, size, is_active)


@router.post("/festivals/{festival_id}/registration-forms/", response_model=RegistrationFormResponse, status_code=201)
async def create_registration_form(
    festival_id: int,
    form: RegistrationFormCreate,
    sections: list[RegistrationFormSectionCreate] | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    data = form.model_dump()
    data["festival_id"] = festival_id
    form_create = RegistrationFormCreate(**data)
    return form_service.create_with_sections(db, form_create, sections or [], created_by=current_user.id)


@router.get("/festivals/{festival_id}/registration-forms/{form_id}", response_model=RegistrationFormResponse)
async def get_registration_form(
    festival_id: int,
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    form = form_service.get(db, form_id)
    if not form or form.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Form not found in this festival")
    return form


@router.put("/festivals/{festival_id}/registration-forms/{form_id}", response_model=RegistrationFormResponse)
async def update_registration_form(
    festival_id: int,
    form_id: int,
    form: RegistrationFormUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    existing = form_service.get(db, form_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found")
    if existing.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Form not found in this festival")
    require_festival_admin(db, current_user, festival_id)
    updated = form_service.update(db, form_id, form)
    return updated


@router.delete("/festivals/{festival_id}/registration-forms/{form_id}")
async def delete_registration_form(
    festival_id: int,
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    existing = form_service.get(db, form_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found")
    if existing.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Form not found in this festival")
    require_festival_admin(db, current_user, festival_id)
    form_service.delete(db, form_id)
    return {"message": "Registration form deleted"}


@router.get("/public/forms/{token}", response_model=RegistrationFormPublicResponse)
async def get_public_form_by_token(token: str, db: Session = Depends(get_db)):
    """Access a registration form via public/unique token (no auth required)."""
    form = form_service.get_public_by_token(db, token)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or link expired")
    return form


@router.post("/public/forms/{token}/register", response_model=FestivalRegistrationResponse)
async def register_via_public_link(
    token: str,
    registration: FestivalRegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Register for a festival through a public/unique link."""
    if not current_user:
        raise HTTPException(status_code=400, detail="Authentication required to complete registration")
    registration.link_token = token
    result = reg_service.register_user(db, current_user.id, registration)
    if not result:
        raise HTTPException(status_code=400, detail="Could not complete registration. Link may be invalid or expired.")
    return result


@router.get("/festivals/{festival_id}/registration-forms/{form_id}/links/", response_model=RegistrationFormLinkPage)
async def list_registration_form_links(
    festival_id: int,
    form_id: int,
    page: int = 1,
    size: int = 20,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return link_service.get_by_form_paginated(db, form_id, page, size, is_active)


@router.post(
    "/festivals/{festival_id}/registration-forms/{form_id}/links/",
    response_model=RegistrationFormLinkResponse,
    status_code=201,
)
async def generate_registration_link(
    festival_id: int,
    form_id: int,
    link: RegistrationFormLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    data = link.model_dump()
    data["form_id"] = form_id
    link_create = RegistrationFormLinkCreate(**data)
    return link_service.generate_link(db, link_create)


@router.get("/festivals/{festival_id}/registrations/", response_model=FestivalRegistrationPage)
async def list_festival_registrations(
    festival_id: int,
    page: int = 1,
    size: int = 20,
    status: str | None = None,
    include_hidden: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    return reg_service.get_by_festival_paginated(db, festival_id, page, size, status, include_hidden)


@router.get("/festivals/{festival_id}/registrations/export/csv")
async def export_festival_registrations_csv(
    festival_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    csv_buffer = export_registrations_csv(festival)
    return StreamingResponse(
        iter([csv_buffer.getvalue().encode("utf-8-sig")]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=registrations.csv"},
    )


@router.get("/festivals/{festival_id}/registrations/export/pdf")
async def export_festival_registrations_pdf(
    festival_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    pdf_bytes = export_registrations_pdf(festival)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=registrations.pdf"},
    )


@router.get("/users/{user_id}/registrations/", response_model=FestivalRegistrationPage)
async def list_user_registrations(
    user_id: int,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return reg_service.get_by_user_paginated(db, user_id, page, size)


@router.put("/registrations/{registration_id}", response_model=FestivalRegistrationResponse)
async def modify_registration(
    registration_id: int,
    reg: FestivalRegistrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allow upper hierarchy to modify any registration they manage."""
    existing = reg_service.get(db, registration_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found")
    require_festival_admin(db, current_user, existing.festival_id)
    result = reg_service.modify_registration(db, registration_id, reg, modified_by=current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Registration not found")
    return result


@router.post("/registrations/{registration_id}/approve", response_model=FestivalRegistrationResponse)
async def approve_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = reg_service.get(db, registration_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found")
    require_festival_admin(db, current_user, existing.festival_id)
    result = reg_service.approve_registration(db, registration_id, approved_by=current_user.id)
    if not result:
        raise HTTPException(status_code=400, detail="Could not approve. Registration may not be pending.")
    return result


@router.post("/registrations/{registration_id}/reject", response_model=FestivalRegistrationResponse)
async def reject_registration(
    registration_id: int,
    reason: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = reg_service.get(db, registration_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found")
    require_festival_admin(db, current_user, existing.festival_id)
    result = reg_service.reject_registration(db, registration_id, rejected_by=current_user.id, reason=reason)
    if not result:
        raise HTTPException(status_code=400, detail="Could not reject. Registration may not be pending.")
    return result


@router.post("/registrations/{registration_id}/payment/mark-paid", response_model=FestivalRegistrationResponse)
async def mark_registration_paid(
    registration_id: int,
    payment: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = reg_service.get(db, registration_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found")
    require_festival_admin(db, current_user, existing.festival_id)
    result = reg_service.mark_paid(db, existing, method=payment.method, transaction_id=payment.transaction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Registration not found")
    return result


@router.post("/registrations/{registration_id}/payment/mark-refunded", response_model=FestivalRegistrationResponse)
async def mark_registration_refunded(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = reg_service.get(db, registration_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found")
    require_festival_admin(db, current_user, existing.festival_id)
    result = reg_service.mark_refunded(db, existing)
    if not result:
        raise HTTPException(status_code=404, detail="Registration not found")
    return result


@router.delete("/registrations/{registration_id}")
async def cancel_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = reg_service.get(db, registration_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found")
    if existing.user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    reg_service.delete(db, registration_id)
    return {"message": "Registration cancelled"}


@router.post("/registration-forms/{form_id}/sections/", response_model=RegistrationFormSectionResponse, status_code=201)
async def create_registration_form_section(
    form_id: int,
    section: RegistrationFormSectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_festival_admin(db, current_user, form.festival_id)
    return section_service.create_with_relations(db, form_id, section)


@router.put("/registration-forms/{form_id}/sections/{section_id}", response_model=RegistrationFormSectionResponse)
async def update_registration_form_section(
    form_id: int,
    section_id: int,
    section: RegistrationFormSectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    existing = section_service.get(db, section_id)
    if not existing or existing.form_id != form_id:
        raise HTTPException(status_code=404, detail="Section not found in form")
    require_festival_admin(db, current_user, form.festival_id)
    updated = section_service.update_with_relations(db, section_id, section)
    return updated


@router.delete("/registration-forms/{form_id}/sections/{section_id}")
async def delete_registration_form_section(
    form_id: int,
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    existing = section_service.get(db, section_id)
    if not existing or existing.form_id != form_id:
        raise HTTPException(status_code=404, detail="Section not found in form")
    require_festival_admin(db, current_user, form.festival_id)
    section_service.delete(db, section_id)
    return {"message": "Section deleted"}
