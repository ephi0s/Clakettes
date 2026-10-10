"""Registration service — business logic for registration forms, links, and festival registrations."""

import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone

from app.enums import PaymentStatus
from app.models.registration import (
    RegistrationForm,
    RegistrationFormSection,
    RegistrationFormSectionRole,
    RegistrationFormSectionTag,
    RegistrationFormLink,
    FestivalRegistration,
    RegistrationSectionSelection,
    RegistrationStatus,
)
from app.schemas.registration import (
    RegistrationFormCreate,
    RegistrationFormUpdate,
    RegistrationFormSectionCreate,
    RegistrationFormSectionUpdate,
    RegistrationFormLinkCreate,
    FestivalRegistrationCreate,
    FestivalRegistrationUpdate,
)
from .base_service import BaseService


class RegistrationFormService(BaseService[RegistrationForm, RegistrationFormCreate, RegistrationFormUpdate]):
    def __init__(self):
        super().__init__(RegistrationForm)

    def get_by_festival(self, db: Session, festival_id: int, is_active: bool | None = None) -> list[RegistrationForm]:
        query = db.query(RegistrationForm).filter(RegistrationForm.festival_id == festival_id)
        if is_active is not None:
            query = query.filter(RegistrationForm.is_active == is_active)
        return query.order_by(RegistrationForm.created_at.desc()).all()

    def get_by_festival_paginated(
        self, db: Session, festival_id: int, page: int, size: int, is_active: bool | None = None
    ) -> dict:
        query = db.query(RegistrationForm).filter(RegistrationForm.festival_id == festival_id)
        if is_active is not None:
            query = query.filter(RegistrationForm.is_active == is_active)
        return self.paginate(query.order_by(RegistrationForm.created_at.desc()), page, size)

    def create_with_sections(
        self,
        db: Session,
        obj_in: RegistrationFormCreate,
        sections: list[RegistrationFormSectionCreate] | None = None,
        created_by: int | None = None,
    ) -> RegistrationForm:
        data = obj_in.model_dump()
        if created_by:
            data["created_by"] = created_by
        db_obj = RegistrationForm(**data)

        if sections:
            for section_data in sections:
                section_dict = section_data.model_dump(exclude={"role_ids", "tag_ids"})
                section = RegistrationFormSection(**section_dict)
                for role_id in section_data.role_ids:
                    section.role_assignments.append(RegistrationFormSectionRole(role_id=role_id))
                for tag_id in section_data.tag_ids:
                    section.tag_assignments.append(RegistrationFormSectionTag(tag_id=tag_id))
                db_obj.sections.append(section)

        try:
            db.add(db_obj)
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(db_obj)
        return db_obj

    def get_public_by_token(self, db: Session, token: str) -> RegistrationForm | None:
        """Get a registration form via a valid public/unique link token."""
        link = (
            db.query(RegistrationFormLink)
            .filter(
                RegistrationFormLink.token == token,
                RegistrationFormLink.is_active,
                or_(
                    RegistrationFormLink.expires_at.is_(None),
                    RegistrationFormLink.expires_at > datetime.now(timezone.utc),
                ),
            )
            .first()
        )
        if not link:
            return None
        form = self.get(db, link.form_id)
        if not form or not form.is_active:
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


class RegistrationFormSectionService(
    BaseService[RegistrationFormSection, RegistrationFormSectionCreate, RegistrationFormSectionUpdate]
):
    def __init__(self):
        super().__init__(RegistrationFormSection)

    def create_with_relations(self, db: Session, form_id: int, obj_in: RegistrationFormSectionCreate):
        role_ids = obj_in.role_ids
        tag_ids = obj_in.tag_ids
        section_dict = obj_in.model_dump(exclude={"role_ids", "tag_ids"})
        section_dict["form_id"] = form_id
        db_obj = RegistrationFormSection(**section_dict)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        for role_id in role_ids:
            sr = RegistrationFormSectionRole(section_id=db_obj.id, role_id=role_id)
            db.add(sr)
        for tag_id in tag_ids:
            st = RegistrationFormSectionTag(section_id=db_obj.id, tag_id=tag_id)
            db.add(st)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_relations(self, db: Session, section_id: int, obj_in: RegistrationFormSectionUpdate):
        existing = db.query(RegistrationFormSection).filter(RegistrationFormSection.id == section_id).first()
        if not existing:
            return None
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"role_ids", "tag_ids"})
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.commit()

        if obj_in.role_ids is not None:
            db.query(RegistrationFormSectionRole).filter(RegistrationFormSectionRole.section_id == section_id).delete()
            for role_id in obj_in.role_ids:
                sr = RegistrationFormSectionRole(section_id=section_id, role_id=role_id)
                db.add(sr)
        if obj_in.tag_ids is not None:
            db.query(RegistrationFormSectionTag).filter(RegistrationFormSectionTag.section_id == section_id).delete()
            for tag_id in obj_in.tag_ids:
                st = RegistrationFormSectionTag(section_id=section_id, tag_id=tag_id)
                db.add(st)

        db.commit()
        db.refresh(existing)
        return existing

    def get_by_form(self, db: Session, form_id: int) -> list[RegistrationFormSection]:
        return (
            db.query(RegistrationFormSection)
            .filter(RegistrationFormSection.form_id == form_id)
            .order_by(RegistrationFormSection.sort_order)
            .all()
        )


class RegistrationFormLinkService(
    BaseService[RegistrationFormLink, RegistrationFormLinkCreate, RegistrationFormLinkCreate]
):
    def __init__(self):
        super().__init__(RegistrationFormLink)

    def generate_link(self, db: Session, obj_in: RegistrationFormLinkCreate) -> RegistrationFormLink:
        token = uuid.uuid4().hex
        data = obj_in.model_dump()
        data["token"] = token
        db_obj = RegistrationFormLink(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def consume_link(self, db: Session, token: str) -> RegistrationFormLink | None:
        """Mark a link as used (for unique links)."""
        link = (
            db.query(RegistrationFormLink)
            .filter(
                RegistrationFormLink.token == token,
                RegistrationFormLink.is_active,
                or_(
                    RegistrationFormLink.expires_at.is_(None),
                    RegistrationFormLink.expires_at > datetime.now(timezone.utc),
                ),
            )
            .first()
        )
        if not link:
            return None

        link.use_count += 1
        if link.is_unique or (link.max_uses and link.use_count >= link.max_uses):
            link.is_active = False

        db.commit()
        db.refresh(link)
        return link

    def get_by_form(self, db: Session, form_id: int, is_active: bool | None = None) -> list[RegistrationFormLink]:
        query = db.query(RegistrationFormLink).filter(RegistrationFormLink.form_id == form_id)
        if is_active is not None:
            query = query.filter(RegistrationFormLink.is_active == is_active)
        return query.all()

    def get_by_form_paginated(
        self, db: Session, form_id: int, page: int, size: int, is_active: bool | None = None
    ) -> dict:
        query = db.query(RegistrationFormLink).filter(RegistrationFormLink.form_id == form_id)
        if is_active is not None:
            query = query.filter(RegistrationFormLink.is_active == is_active)
        return self.paginate(query, page, size)


class FestivalRegistrationService(
    BaseService[FestivalRegistration, FestivalRegistrationCreate, FestivalRegistrationUpdate]
):
    def __init__(self):
        super().__init__(FestivalRegistration)

    def register_user(
        self, db: Session, user_id: int, obj_in: FestivalRegistrationCreate
    ) -> FestivalRegistration | None:
        """Register a user through a form link."""
        link = (
            db.query(RegistrationFormLink)
            .filter(
                RegistrationFormLink.token == obj_in.link_token,
                RegistrationFormLink.is_active,
                or_(
                    RegistrationFormLink.expires_at.is_(None),
                    RegistrationFormLink.expires_at > datetime.now(timezone.utc),
                ),
            )
            .first()
        )
        if not link:
            return None

        form = (
            db.query(RegistrationForm).filter(RegistrationForm.id == link.form_id, RegistrationForm.is_active).first()
        )
        if not form:
            return None

        # For unique links, check user matches
        if link.is_unique and link.assigned_user_id and link.assigned_user_id != user_id:
            return None

        # Check max registrations
        if form.max_registrations:
            count = (
                db.query(FestivalRegistration)
                .filter(
                    FestivalRegistration.form_id == form.id,
                    FestivalRegistration.status.in_(
                        [RegistrationStatus.PENDING.value, RegistrationStatus.APPROVED.value]
                    ),
                )
                .count()
            )
            if count >= form.max_registrations:
                return None

        # Create registration
        reg = FestivalRegistration(
            user_id=user_id,
            festival_id=form.festival_id,
            form_id=form.id,
            link_id=link.id,
            status=RegistrationStatus.PENDING.value,
            payment_status=(PaymentStatus.PENDING.value if (form.fee_amount or 0) > 0 else PaymentStatus.PAID.value),
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        # Process section selections
        for sel in obj_in.sections:
            section = (
                db.query(RegistrationFormSection)
                .filter(RegistrationFormSection.id == sel.section_id, RegistrationFormSection.form_id == form.id)
                .first()
            )
            if not section:
                continue

            # Verify role is valid for this section
            if sel.role_id:
                valid_role = (
                    db.query(RegistrationFormSectionRole)
                    .filter(
                        RegistrationFormSectionRole.section_id == section.id,
                        RegistrationFormSectionRole.role_id == sel.role_id,
                    )
                    .first()
                )
                if not valid_role:
                    continue

            # Verify tags are valid for this section
            valid_tag_ids = set()
            if sel.additional_tag_ids:
                valid_tags = (
                    db.query(RegistrationFormSectionTag)
                    .filter(
                        RegistrationFormSectionTag.section_id == section.id,
                        RegistrationFormSectionTag.tag_id.in_(sel.additional_tag_ids),
                    )
                    .all()
                )
                valid_tag_ids = {vt.tag_id for vt in valid_tags}

            selection = RegistrationSectionSelection(
                registration_id=reg.id,
                section_id=sel.section_id,
                role_id=sel.role_id,
                additional_tags=list(valid_tag_ids) if valid_tag_ids else None,
            )
            db.add(selection)

        db.commit()
        db.refresh(reg)

        # Increment link usage
        link.use_count += 1
        if link.is_unique or (link.max_uses and link.use_count >= link.max_uses):
            link.is_active = False
        db.commit()

        return reg

    def get_by_festival(
        self, db: Session, festival_id: int, status: str | None = None, include_hidden: bool = False
    ) -> list[FestivalRegistration]:
        query = db.query(FestivalRegistration).filter(FestivalRegistration.festival_id == festival_id)
        if status:
            query = query.filter(FestivalRegistration.status == status)
        if not include_hidden:
            query = query.filter(~FestivalRegistration.is_hidden)
        return query.order_by(FestivalRegistration.created_at.desc()).all()

    def get_by_festival_paginated(
        self,
        db: Session,
        festival_id: int,
        page: int,
        size: int,
        status: str | None = None,
        include_hidden: bool = False,
    ) -> dict:
        query = db.query(FestivalRegistration).filter(FestivalRegistration.festival_id == festival_id)
        if status:
            query = query.filter(FestivalRegistration.status == status)
        if not include_hidden:
            query = query.filter(~FestivalRegistration.is_hidden)
        return self.paginate(query.order_by(FestivalRegistration.created_at.desc()), page, size)

    def get_by_user(self, db: Session, user_id: int) -> list[FestivalRegistration]:
        return (
            db.query(FestivalRegistration)
            .filter(FestivalRegistration.user_id == user_id)
            .order_by(FestivalRegistration.created_at.desc())
            .all()
        )

    def get_by_user_paginated(self, db: Session, user_id: int, page: int, size: int) -> dict:
        query = db.query(FestivalRegistration).filter(FestivalRegistration.user_id == user_id)
        return self.paginate(query.order_by(FestivalRegistration.created_at.desc()), page, size)

    def approve_registration(self, db: Session, registration_id: int, approved_by: int) -> FestivalRegistration | None:
        reg = self.get(db, registration_id)
        if not reg or reg.status != RegistrationStatus.PENDING:
            return None
        if reg.payment_status != PaymentStatus.PAID.value:
            raise HTTPException(status_code=409, detail="Payment required for this registration")
        reg.status = RegistrationStatus.APPROVED.value
        reg.approved_by = approved_by
        reg.approved_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(reg)

        # Auto-create UserRole and UserParticipantTag based on selections
        for sel in reg.selections:
            if sel.role_id:
                from app.models.user_role import UserRole, UserRoleStatus

                existing_role = (
                    db.query(UserRole)
                    .filter(
                        UserRole.user_id == reg.user_id,
                        UserRole.role_id == sel.role_id,
                        UserRole.festival_id == reg.festival_id,
                        UserRole.status == UserRoleStatus.APPROVED.value,
                    )
                    .first()
                )
                if not existing_role:
                    ur = UserRole(
                        user_id=reg.user_id,
                        role_id=sel.role_id,
                        festival_id=reg.festival_id,
                        status=UserRoleStatus.APPROVED.value,
                        assigned_by=approved_by,
                        approved_by=approved_by,
                        approved_at=datetime.now(timezone.utc),
                    )
                    db.add(ur)

            if sel.additional_tags:
                from app.models.user_role import UserParticipantTag

                for tag_id in sel.additional_tags:
                    existing_tag = (
                        db.query(UserParticipantTag)
                        .filter(
                            UserParticipantTag.user_id == reg.user_id,
                            UserParticipantTag.tag_id == tag_id,
                            UserParticipantTag.festival_id == reg.festival_id,
                        )
                        .first()
                    )
                    if not existing_tag:
                        upt = UserParticipantTag(
                            user_id=reg.user_id,
                            tag_id=tag_id,
                            festival_id=reg.festival_id,
                            is_primary=(tag_id == sel.additional_tags[0]),
                            assigned_by=approved_by,
                        )
                        db.add(upt)

        db.commit()
        db.refresh(reg)
        return reg

    def reject_registration(
        self, db: Session, registration_id: int, rejected_by: int, reason: str | None = None
    ) -> FestivalRegistration | None:
        reg = self.get(db, registration_id)
        if not reg or reg.status != RegistrationStatus.PENDING:
            return None
        reg.status = RegistrationStatus.REJECTED.value
        reg.approved_by = rejected_by
        reg.approved_at = datetime.now(timezone.utc)
        if reason:
            reg.notes = (reg.notes or "") + f"\nRejected: {reason}"
        db.commit()
        db.refresh(reg)
        return reg

    def mark_paid(
        self,
        db: Session,
        registration: FestivalRegistration,
        method: str | None = None,
        transaction_id: str | None = None,
    ) -> FestivalRegistration | None:
        """Mark a registration as paid (manual/offline payment recorded by an admin)."""
        if not registration:
            return None
        registration.payment_status = PaymentStatus.PAID.value
        registration.paid_at = datetime.now(timezone.utc)
        if method:
            registration.payment_method = method
        if transaction_id:
            registration.transaction_id = transaction_id
        db.commit()
        db.refresh(registration)
        return registration

    def mark_refunded(self, db: Session, registration: FestivalRegistration) -> FestivalRegistration | None:
        """Mark a registration's payment as refunded."""
        if not registration:
            return None
        registration.payment_status = PaymentStatus.REFUNDED.value
        db.commit()
        db.refresh(registration)
        return registration

    def modify_registration(
        self, db: Session, registration_id: int, obj_in: FestivalRegistrationUpdate, modified_by: int
    ) -> FestivalRegistration | None:
        """Allow upper hierarchy to modify any registration they manage."""
        reg = self.get(db, registration_id)
        if not reg:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reg, field, value)
        reg.assigned_by = modified_by
        db.commit()
        db.refresh(reg)
        return reg

    def get_user_registrations_in_festival(
        self, db: Session, user_id: int, festival_id: int
    ) -> list[FestivalRegistration]:
        """Get all registrations for a user in a specific festival."""
        return (
            db.query(FestivalRegistration)
            .filter(
                FestivalRegistration.user_id == user_id,
                FestivalRegistration.festival_id == festival_id,
            )
            .all()
        )
