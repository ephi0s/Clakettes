"""Router for form definitions, pages, fields, responses, and links."""

from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.form_definition import (
    FormDefinitionCreate,
    FormDefinitionUpdate,
    FormDefinitionResponse,
    FormDefinitionPublicResponse,
    FormDefinitionPage,
    FormPageCreate,
    FormPageUpdate,
    FormPageResponse,
    FormFieldCreate,
    FormFieldUpdate,
    FormFieldResponse,
    FormLinkCreate,
    FormLinkResponse,
    FormLinkPage,
    FormResponseCreate,
    FormResponseUpdate,
    FormResponseResponse,
    FormResponsePage,
    FormCloneRequest,
)
from app.services.form_service import (
    FormDefinitionService,
    FormPageService,
    FormFieldService,
    FormResponseService,
    FormLinkService,
)
from app.services.export_service import export_form_responses_csv
from app.routers.permissions import require_form_admin
from app.routers.dependencies import get_current_user_optional, get_or_404
from app.models.user import User
from app.models.form_definition import FormDefinition, FormPage, FormField, FormFieldOption, FormResponse

router = APIRouter()

form_service = FormDefinitionService()
page_service = FormPageService()
field_service = FormFieldService()
response_service = FormResponseService()
link_service = FormLinkService()


@router.get("/forms/", response_model=FormDefinitionPage)
async def list_forms(
    form_type: str | None = None,
    festival_id: int | None = None,
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(form_service.model)
    if form_type:
        query = query.filter(form_service.model.form_type == form_type)
    if festival_id is not None:
        query = query.filter(form_service.model.festival_id == festival_id)
    if is_active is not None:
        query = query.filter(form_service.model.is_active == is_active)
    query = query.order_by(form_service.model.sort_order, form_service.model.created_at.desc())
    result = form_service.paginate(query, page, size)
    return result


@router.post("/forms/", response_model=FormDefinitionResponse, status_code=201)
async def create_form(
    form: FormDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return form_service.create_with_pages(db, form, user_id=current_user.id)


@router.get("/forms/{form_id}", response_model=FormDefinitionResponse)
async def get_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_404(db, FormDefinition, form_id, "Form")


@router.put("/forms/{form_id}", response_model=FormDefinitionResponse)
async def update_form(
    form_id: int,
    form: FormDefinitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, FormDefinition, form_id, "Form")
    require_form_admin(db, current_user, existing)
    updated = form_service.update(db, form_id, form)
    return updated


@router.delete("/forms/{form_id}")
async def delete_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = form_service.get(db, form_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, existing)
    form_service.delete(db, form_id)
    return {"message": "Form deleted"}


@router.post("/forms/{form_id}/clone", response_model=FormDefinitionResponse)
async def clone_form(
    form_id: int,
    body: FormCloneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = form_service.get(db, form_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, existing)
    cloned = form_service.clone_form(db, form_id, new_title=body.title)
    return cloned


@router.post("/forms/{form_id}/pages/", response_model=FormPageResponse, status_code=201)
async def create_page(
    form_id: int,
    page: FormPageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    page_dict = page.model_dump(exclude={"fields"})
    page_dict["form_id"] = form_id
    fields_data = page.fields or []
    db_page = FormPage(**page_dict)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    for field_data in fields_data:
        options_data = field_data.options or []
        field_dict = field_data.model_dump(exclude={"options"})
        field_dict["page_id"] = db_page.id
        field = FormField(**field_dict)
        db.add(field)
        db.commit()
        db.refresh(field)
        for opt_data in options_data:
            opt = FormFieldOption(**opt_data.model_dump(), field_id=field.id)
            db.add(opt)
        db.commit()
    db.refresh(db_page)
    return db_page


@router.put("/forms/{form_id}/pages/{page_id}", response_model=FormPageResponse)
async def update_page(
    form_id: int,
    page_id: int,
    page: FormPageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    existing = page_service.get(db, page_id)
    if not existing or existing.form_id != form_id:
        raise HTTPException(status_code=404, detail="Page not found in form")
    updated = page_service.update(db, page_id, page)
    return updated


@router.delete("/forms/{form_id}/pages/{page_id}")
async def delete_page(
    form_id: int,
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    existing = page_service.get(db, page_id)
    if not existing or existing.form_id != form_id:
        raise HTTPException(status_code=404, detail="Page not found in form")
    page_service.delete(db, page_id)
    return {"message": "Page deleted"}


@router.post("/forms/{form_id}/pages/{page_id}/fields/", response_model=FormFieldResponse, status_code=201)
async def create_field(
    form_id: int,
    page_id: int,
    field: FormFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    page = page_service.get(db, page_id)
    if not page or page.form_id != form_id:
        raise HTTPException(status_code=404, detail="Page not found in form")
    options_data = field.options or []
    field_dict = field.model_dump(exclude={"options"})
    field_dict["page_id"] = page_id
    db_field = FormField(**field_dict)
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    for opt_data in options_data:
        opt = FormFieldOption(**opt_data.model_dump(), field_id=db_field.id)
        db.add(opt)
    db.commit()
    db.refresh(db_field)
    return db_field


@router.put("/forms/{form_id}/fields/{field_id}", response_model=FormFieldResponse)
async def update_field(
    form_id: int,
    field_id: int,
    field: FormFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    existing = field_service.get(db, field_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Field not found")
    updated = field_service.update(db, field_id, field)
    return updated


@router.delete("/forms/{form_id}/fields/{field_id}")
async def delete_field(
    form_id: int,
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    existing = field_service.get(db, field_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Field not found")
    field_service.delete(db, field_id)
    return {"message": "Field deleted"}


@router.get("/forms/{form_id}/links/", response_model=FormLinkPage)
async def list_form_links(
    form_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    return link_service.get_by_form_paginated(db, form_id, page, size, is_active)


@router.post("/forms/{form_id}/links/", response_model=FormLinkResponse, status_code=201)
async def create_form_link(
    form_id: int,
    link: FormLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    return link_service.generate_link(db, link, form_id=form_id)


@router.delete("/forms/{form_id}/links/{link_id}")
async def delete_form_link(
    form_id: int,
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    existing = link_service.get(db, link_id)
    if not existing or existing.form_id != form_id:
        raise HTTPException(status_code=404, detail="Link not found")
    link_service.delete(db, link_id)
    return {"message": "Link deleted"}


@router.get("/forms/public/{token}", response_model=FormDefinitionPublicResponse)
async def get_public_form(token: str, db: Session = Depends(get_db)):
    form = form_service.get_public_form(db, token)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or link expired")
    return form


@router.post("/forms/public/{token}/submit", response_model=FormResponseResponse)
async def submit_public_response(
    token: str,
    response: FormResponseCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    form = form_service.get_by_token(db, token)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or link invalid")
    if form.require_auth and not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_id = current_user.id if current_user else None
    result = response_service.submit_response(db, form.id, user_id, response.field_values, link_token=token)
    if not result:
        raise HTTPException(status_code=400, detail="Could not submit response. Form may be full or inactive.")
    return result


@router.get("/forms/{form_id}/responses/", response_model=FormResponsePage)
async def list_form_responses(
    form_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    query = db.query(FormResponse).filter(FormResponse.form_id == form_id)
    if status:
        query = query.filter(FormResponse.status == status)
    query = query.order_by(FormResponse.created_at.desc())
    return response_service.paginate(query, page, size)


@router.get("/forms/{form_id}/responses/export/csv")
async def export_form_responses_csv_endpoint(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = form_service.get(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    csv_buffer = export_form_responses_csv(db, form_id)
    return StreamingResponse(
        iter([csv_buffer.getvalue().encode("utf-8-sig")]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=form_{form_id}_responses.csv"},
    )


@router.put("/forms/responses/{response_id}", response_model=FormResponseResponse)
async def update_form_response(
    response_id: int,
    response: FormResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = response_service.get(db, response_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Response not found")
    form = form_service.get(db, existing.form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    updated = response_service.update(db, response_id, response)
    return updated


@router.post("/forms/responses/{response_id}/approve", response_model=FormResponseResponse)
async def approve_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = response_service.get(db, response_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Response not found")
    form = form_service.get(db, existing.form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    result = response_service.approve_response(db, response_id, reviewer_id=current_user.id)
    if not result:
        raise HTTPException(status_code=400, detail="Could not approve. Response may not be in draft status.")
    return result


@router.post("/forms/responses/{response_id}/reject", response_model=FormResponseResponse)
async def reject_response(
    response_id: int,
    reason: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = response_service.get(db, response_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Response not found")
    form = form_service.get(db, existing.form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_form_admin(db, current_user, form)
    result = response_service.reject_response(db, response_id, reviewer_id=current_user.id, reason=reason)
    if not result:
        raise HTTPException(status_code=400, detail="Could not reject. Response may not be in draft status.")
    return result


# Import models for direct use in endpoints that create nested objects
