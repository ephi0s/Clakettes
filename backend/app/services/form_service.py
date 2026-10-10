"""Form service — business logic for form definitions, pages, fields, responses, and links."""

import uuid

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Any
from datetime import datetime, timezone

from app.models.form_definition import (
    FormDefinition,
    FormPage,
    FormField,
    FormFieldOption,
    FormResponse,
    FormFieldResponse,
    FormLink,
    SubmissionStatus,
)
from app.schemas.form_definition import (
    FormDefinitionCreate,
    FormDefinitionUpdate,
    FormPageCreate,
    FormPageUpdate,
    FormFieldCreate,
    FormFieldUpdate,
    FormResponseCreate,
    FormResponseUpdate,
    FormLinkCreate,
)
from .base_service import BaseService


class FormDefinitionService(BaseService[FormDefinition, FormDefinitionCreate, FormDefinitionUpdate]):
    def __init__(self):
        super().__init__(FormDefinition)

    def create_with_pages(
        self,
        db: Session,
        obj_in: FormDefinitionCreate,
        user_id: int | None = None,
    ) -> FormDefinition:
        data = obj_in.model_dump(exclude={"pages"})
        if user_id:
            data["created_by"] = user_id
        db_obj = FormDefinition(**data)

        if obj_in.pages:
            for page_data in obj_in.pages:
                page_dict = page_data.model_dump(exclude={"fields"})
                page = FormPage(**page_dict)
                for field_data in page_data.fields or []:
                    field_dict = field_data.model_dump(exclude={"options"})
                    field = FormField(**field_dict)
                    for opt_data in field_data.options or []:
                        field.options.append(FormFieldOption(**opt_data.model_dump()))
                    page.fields.append(field)
                db_obj.pages.append(page)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_token(self, db: Session, token: str) -> FormDefinition | None:
        link = (
            db.query(FormLink)
            .filter(
                FormLink.token == token,
                FormLink.is_active,
                or_(
                    FormLink.expires_at.is_(None),
                    FormLink.expires_at > datetime.now(timezone.utc),
                ),
            )
            .first()
        )
        if not link:
            return None
        return self.get(db, link.form_id)

    def clone_form(self, db: Session, form_id: int, new_title: str | None = None) -> FormDefinition:
        from sqlalchemy.orm import selectinload

        original = (
            db.query(FormDefinition)
            .options(selectinload(FormDefinition.pages).selectinload(FormPage.fields).selectinload(FormField.options))
            .filter(FormDefinition.id == form_id)
            .first()
        )
        if not original:
            raise ValueError("Form not found")

        title = new_title if new_title else f"{original.title} (Copy)"
        now = datetime.now(timezone.utc)
        clone = FormDefinition(
            title=title,
            description=original.description,
            form_type=original.form_type,
            festival_id=original.festival_id,
            is_active=original.is_active,
            is_public=original.is_public,
            starts_at=original.starts_at,
            ends_at=original.ends_at,
            max_submissions=original.max_submissions,
            require_auth=original.require_auth,
            requires_approval=original.requires_approval,
            success_message=original.success_message,
            submit_button_text=original.submit_button_text,
            created_by=original.created_by,
            settings=original.settings,
            sort_order=original.sort_order,
            created_at=now,
            updated_at=now,
        )
        db.add(clone)
        db.flush()

        for page in original.pages:
            new_page = FormPage(
                form_id=clone.id,
                title=page.title,
                description=page.description,
                sort_order=page.sort_order,
                is_repeatable=page.is_repeatable,
                created_at=now,
                updated_at=now,
            )
            db.add(new_page)
            db.flush()
            for field in page.fields:
                new_field = FormField(
                    page_id=new_page.id,
                    field_type=field.field_type,
                    label=field.label,
                    help_text=field.help_text,
                    placeholder=field.placeholder,
                    is_required=field.is_required,
                    is_visible=field.is_visible,
                    is_read_only=field.is_read_only,
                    sort_order=field.sort_order,
                    default_value=field.default_value,
                    min_length=field.min_length,
                    max_length=field.max_length,
                    min_value=field.min_value,
                    max_value=field.max_value,
                    regex_pattern=field.regex_pattern,
                    error_message=field.error_message,
                    allowed_values=field.allowed_values,
                    depends_on_field_id=None,
                    depends_on_value=field.depends_on_value,
                    role_filter=field.role_filter,
                    settings=field.settings,
                    width_class=field.width_class,
                    created_at=now,
                    updated_at=now,
                )
                db.add(new_field)
                db.flush()
                for opt in field.options:
                    new_opt = FormFieldOption(
                        field_id=new_field.id,
                        value=opt.value,
                        label=opt.label,
                        sort_order=opt.sort_order,
                    )
                    db.add(new_opt)
        db.commit()
        db.refresh(clone)
        return (
            db.query(FormDefinition)
            .options(selectinload(FormDefinition.pages).selectinload(FormPage.fields).selectinload(FormField.options))
            .filter(FormDefinition.id == clone.id)
            .first()
        )

    def get_public_form(self, db: Session, token: str) -> FormDefinition | None:
        link = (
            db.query(FormLink)
            .filter(
                FormLink.token == token,
                FormLink.is_active,
                or_(
                    FormLink.expires_at.is_(None),
                    FormLink.expires_at > datetime.now(timezone.utc),
                ),
            )
            .first()
        )
        if not link:
            return None
        form = self.get(db, link.form_id)
        if not form or not form.is_active or not form.is_public:
            return None
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        ends_at = form.ends_at
        if ends_at and ends_at.tzinfo is not None:
            ends_at = ends_at.replace(tzinfo=None)
        if ends_at and ends_at < now:
            return None
        starts_at = form.starts_at
        if starts_at and starts_at.tzinfo is not None:
            starts_at = starts_at.replace(tzinfo=None)
        if starts_at and starts_at > now:
            return None
        return form


class FormPageService(BaseService[FormPage, FormPageCreate, FormPageUpdate]):
    def __init__(self):
        super().__init__(FormPage)


class FormFieldService(BaseService[FormField, FormFieldCreate, FormFieldUpdate]):
    def __init__(self):
        super().__init__(FormField)


class FormResponseService(BaseService[FormResponse, FormResponseCreate, FormResponseUpdate]):
    def __init__(self):
        super().__init__(FormResponse)

    def submit_response(
        self,
        db: Session,
        form_id: int,
        user_id: int | None,
        field_values: dict[str, Any],
        link_token: str | None = None,
    ) -> FormResponse | None:
        form = db.query(FormDefinition).filter(FormDefinition.id == form_id, FormDefinition.is_active).first()
        if not form:
            return None

        if link_token:
            link = (
                db.query(FormLink)
                .filter(
                    FormLink.token == link_token,
                    FormLink.form_id == form_id,
                    FormLink.is_active,
                    or_(
                        FormLink.expires_at.is_(None),
                        FormLink.expires_at > datetime.now(timezone.utc),
                    ),
                )
                .first()
            )
            if not link:
                return None

        if form.max_submissions:
            count = (
                db.query(FormResponse)
                .filter(
                    FormResponse.form_id == form_id,
                    FormResponse.status.in_([SubmissionStatus.SUBMITTED.value, SubmissionStatus.APPROVED.value]),
                )
                .count()
            )
            if count >= form.max_submissions:
                return None

        response = FormResponse(
            form_id=form_id,
            user_id=user_id,
            festival_id=form.festival_id,
            status=SubmissionStatus.SUBMITTED if not form.requires_approval else SubmissionStatus.DRAFT,
            submitted_at=datetime.now(timezone.utc),
            link_token=link_token,
        )
        db.add(response)
        db.commit()
        db.refresh(response)

        fields = (
            db.query(FormField)
            .filter(FormField.page_id.in_(db.query(FormPage.id).filter(FormPage.form_id == form_id)))
            .all()
        )
        field_map = {f.id: f for f in fields}

        for key, value in field_values.items():
            try:
                field_id = int(key)
            except (ValueError, TypeError):
                continue
            if field_id not in field_map:
                continue
            fr = FormFieldResponse(
                response_id=response.id,
                field_id=field_id,
                value=value,
            )
            db.add(fr)

        db.commit()
        db.refresh(response)

        if link_token:
            link = db.query(FormLink).filter(FormLink.token == link_token).first()
            if link:
                link.use_count += 1
                if link.is_unique or (link.max_uses and link.use_count >= link.max_uses):
                    link.is_active = False
                db.commit()

        return response

    def approve_response(self, db: Session, response_id: int, reviewer_id: int) -> FormResponse | None:
        resp = self.get(db, response_id)
        if not resp or resp.status != SubmissionStatus.DRAFT:
            return None
        resp.status = SubmissionStatus.APPROVED
        resp.reviewer_id = reviewer_id
        resp.reviewed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(resp)
        return resp

    def reject_response(
        self, db: Session, response_id: int, reviewer_id: int, reason: str | None = None
    ) -> FormResponse | None:
        resp = self.get(db, response_id)
        if not resp or resp.status != SubmissionStatus.DRAFT:
            return None
        resp.status = SubmissionStatus.REJECTED
        resp.reviewer_id = reviewer_id
        resp.reviewed_at = datetime.now(timezone.utc)
        if reason:
            resp.review_notes = (resp.review_notes or "") + f"\nRejected: {reason}"
        db.commit()
        db.refresh(resp)
        return resp


class FormLinkService(BaseService[FormLink, FormLinkCreate, FormLinkCreate]):
    def __init__(self):
        super().__init__(FormLink)

    def generate_link(self, db: Session, obj_in: FormLinkCreate, form_id: int) -> FormLink:
        token = uuid.uuid4().hex
        data = obj_in.model_dump()
        data["token"] = token
        data["form_id"] = form_id
        db_obj = FormLink(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_form_paginated(
        self, db: Session, form_id: int, page: int, size: int, is_active: bool | None = None
    ) -> dict:
        query = db.query(FormLink).filter(FormLink.form_id == form_id)
        if is_active is not None:
            query = query.filter(FormLink.is_active == is_active)
        return self.paginate(query, page, size)
