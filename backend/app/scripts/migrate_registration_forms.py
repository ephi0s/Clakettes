"""Migrate legacy RegistrationForm system to unified FormDefinition system.

Maps:
  RegistrationForm        -> FormDefinition (type=internal)
  RegistrationFormSection -> FormPage
  Section roles/tags      -> FormField (role_selector / tag_selector)
  RegistrationFormLink    -> FormLink
  FestivalRegistration    -> FormResponse
  RegistrationSectionSelection -> FormFieldResponse

Usage:
    python -m app.scripts.migrate_registration_forms
    python -m app.scripts.migrate_registration_forms --dry-run
"""

import argparse
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.enums import FormType, FormFieldType, SubmissionStatus

from app.models.registration import (
    RegistrationForm,
    RegistrationFormSection,
    RegistrationFormSectionRole,
    RegistrationFormSectionTag,
    RegistrationFormLink,
    FestivalRegistration,
    RegistrationSectionSelection,
)
from app.models.form_definition import (
    FormDefinition,
    FormPage,
    FormField,
    FormFieldOption,
    FormResponse,
    FormFieldResponse,
    FormLink,
)
from app.models.role import Role
from app.models.participant_tag import ParticipantTag


def get_role_field_type(section: RegistrationFormSection) -> FormFieldType:
    return FormFieldType.ROLE_SELECTOR if section.allow_multiple_roles else FormFieldType.ROLE_SELECTOR


def get_tag_field_type(section: RegistrationFormSection) -> FormFieldType:
    return FormFieldType.TAG_SELECTOR


def map_status(status_str: str) -> SubmissionStatus:
    mapping = {
        "pending": SubmissionStatus.SUBMITTED,
        "approved": SubmissionStatus.APPROVED,
        "rejected": SubmissionStatus.REJECTED,
        "waitlisted": SubmissionStatus.SUBMITTED,
        "cancelled": SubmissionStatus.DRAFT,
    }
    return mapping.get(status_str, SubmissionStatus.SUBMITTED)


def migrate(db: Session, dry_run: bool = False):
    """Execute the migration from legacy registration forms to new form definitions."""

    # ------------------------------------------------------------------ #
    # 1. Migrate RegistrationForm -> FormDefinition + Pages + Fields     #
    # ------------------------------------------------------------------ #
    legacy_forms = db.query(RegistrationForm).all()
    print(f"Found {len(legacy_forms)} RegistrationForm(s) to migrate")

    form_id_map = {}  # legacy form_id -> new form_id

    for lf in legacy_forms:
        if dry_run:
            print(f"  [DRY-RUN] Would create FormDefinition from RegistrationForm id={lf.id} title='{lf.title}'")
            form_id_map[lf.id] = None
            continue

        fd = FormDefinition(
            id=lf.id,
            title=lf.title,
            description=lf.description,
            form_type=FormType.INTERNAL,
            festival_id=lf.festival_id,
            is_active=lf.is_active,
            starts_at=lf.starts_at,
            ends_at=lf.ends_at,
            max_submissions=lf.max_registrations,
            require_auth=lf.require_existing_account,
            created_by=lf.created_by,
        )
        db.add(fd)
        db.flush()
        form_id_map[lf.id] = fd.id

        # 1a. Migrate sections -> pages
        sections = (
            db.query(RegistrationFormSection)
            .filter(RegistrationFormSection.form_id == lf.id)
            .order_by(RegistrationFormSection.sort_order)
            .all()
        )

        for sec in sections:
            page = FormPage(
                id=sec.id,
                form_id=fd.id,
                title=sec.title,
                description=sec.description,
                sort_order=sec.sort_order,
                is_repeatable=sec.allow_multiple_roles,
            )
            db.add(page)
            db.flush()

            field_sort = 0

            # 1b. Section roles -> FormField (role_selector)
            role_assignments = (
                db.query(RegistrationFormSectionRole)
                .filter(RegistrationFormSectionRole.section_id == sec.id)
                .order_by(RegistrationFormSectionRole.sort_order)
                .all()
            )

            if role_assignments:
                role_field = FormField(
                    page_id=page.id,
                    field_type=FormFieldType.ROLE_SELECTOR,
                    label=f"{sec.title} — Role",
                    help_text=f"Select a role for {sec.title}",
                    is_required=sec.is_required,
                    sort_order=field_sort,
                )
                db.add(role_field)
                db.flush()
                field_sort += 1

                for ra in role_assignments:
                    role = db.query(Role).filter(Role.id == ra.role_id).first()
                    if not role:
                        continue
                    opt = FormFieldOption(
                        field_id=role_field.id,
                        value=role.name.lower().replace(" ", "_"),
                        label=role.name,
                        sort_order=ra.sort_order,
                    )
                    db.add(opt)

            # 1c. Section tags -> FormField (tag_selector)
            tag_assignments = (
                db.query(RegistrationFormSectionTag)
                .filter(RegistrationFormSectionTag.section_id == sec.id)
                .order_by(RegistrationFormSectionTag.sort_order)
                .all()
            )

            if tag_assignments:
                tag_field = FormField(
                    page_id=page.id,
                    field_type=FormFieldType.TAG_SELECTOR,
                    label=f"{sec.title} — Tags",
                    help_text=f"Select tags for {sec.title}",
                    is_required=any(ta.is_required for ta in tag_assignments),
                    sort_order=field_sort,
                )
                db.add(tag_field)
                db.flush()
                field_sort += 1

                for ta in tag_assignments:
                    tag = db.query(ParticipantTag).filter(ParticipantTag.id == ta.tag_id).first()
                    if not tag:
                        continue
                    opt = FormFieldOption(
                        field_id=tag_field.id,
                        value=tag.name.lower().replace(" ", "_"),
                        label=tag.name,
                        sort_order=ta.sort_order,
                    )
                    db.add(opt)

        db.flush()
        print(f"  Created FormDefinition id={fd.id} from RegistrationForm id={lf.id}")

    # ------------------------------------------------------------------ #
    # 2. Migrate RegistrationFormLink -> FormLink                       #
    # ------------------------------------------------------------------ #
    legacy_links = db.query(RegistrationFormLink).all()
    print(f"\nFound {len(legacy_links)} RegistrationFormLink(s) to migrate")

    link_id_map = {}  # legacy link_id -> new link_id

    for ll in legacy_links:
        new_form_id = form_id_map.get(ll.form_id)
        if new_form_id is None and not dry_run:
            print(f"  SKIP RegistrationFormLink id={ll.id}: parent form not migrated")
            continue

        if dry_run:
            print(f"  [DRY-RUN] Would create FormLink from RegistrationFormLink id={ll.id}")
            link_id_map[ll.id] = None
            continue

        fl = FormLink(
            id=ll.id,
            form_id=new_form_id,
            token=ll.token,
            is_unique=ll.is_unique,
            is_public=ll.is_public,
            is_active=ll.is_active,
            expires_at=ll.expires_at,
            max_uses=ll.max_uses,
            use_count=ll.use_count,
            assigned_user_id=ll.assigned_user_id,
            notes=ll.notes,
        )
        db.add(fl)
        db.flush()
        link_id_map[ll.id] = fl.id
        print(f"  Created FormLink id={fl.id} from RegistrationFormLink id={ll.id}")

    # ------------------------------------------------------------------ #
    # 3. Migrate FestivalRegistration -> FormResponse                    #
    # ------------------------------------------------------------------ #
    legacy_registrations = db.query(FestivalRegistration).all()
    print(f"\nFound {len(legacy_registrations)} FestivalRegistration(s) to migrate")

    reg_id_map = {}  # legacy registration_id -> new response_id

    for lr in legacy_registrations:
        new_form_id = form_id_map.get(lr.form_id)
        link_id_map.get(lr.link_id)

        if dry_run:
            print(f"  [DRY-RUN] Would create FormResponse from FestivalRegistration id={lr.id}")
            reg_id_map[lr.id] = None
            continue

        resp = FormResponse(
            id=lr.id,
            form_id=new_form_id or lr.form_id,
            user_id=lr.user_id,
            festival_id=lr.festival_id,
            status=map_status(lr.status.value if hasattr(lr.status, "value") else lr.status),
            submitted_at=lr.created_at,
            reviewer_id=lr.approved_by,
            reviewed_at=lr.approved_at,
            review_notes=lr.notes,
            link_token=db.query(RegistrationFormLink).filter(RegistrationFormLink.id == lr.link_id).first().token
            if lr.link_id
            else None,
        )
        db.add(resp)
        db.flush()
        reg_id_map[lr.id] = resp.id
        print(f"  Created FormResponse id={resp.id} from FestivalRegistration id={lr.id}")

        # 3a. Migrate RegistrationSectionSelection -> FormFieldResponse
        selections = (
            db.query(RegistrationSectionSelection).filter(RegistrationSectionSelection.registration_id == lr.id).all()
        )

        for sel in selections:
            section = db.query(RegistrationFormSection).filter(RegistrationFormSection.id == sel.section_id).first()
            if not section:
                continue

            page = (
                db.query(FormPage)
                .filter(
                    FormPage.id == sel.section_id,
                    FormPage.form_id == (new_form_id or lr.form_id),
                )
                .first()
            )
            if not page:
                continue

            role_field = (
                db.query(FormField)
                .filter(
                    FormField.page_id == page.id,
                    FormField.field_type == FormFieldType.ROLE_SELECTOR,
                )
                .first()
            )
            tag_field = (
                db.query(FormField)
                .filter(
                    FormField.page_id == page.id,
                    FormField.field_type == FormFieldType.TAG_SELECTOR,
                )
                .first()
            )

            if role_field and sel.role_id:
                role = db.query(Role).filter(Role.id == sel.role_id).first()
                if role:
                    ffv = FormFieldResponse(
                        response_id=resp.id,
                        field_id=role_field.id,
                        value=role.name.lower().replace(" ", "_"),
                    )
                    db.add(ffv)

            if tag_field and sel.additional_tags:
                tag_values = []
                for tag_id in sel.additional_tags or []:
                    tag = db.query(ParticipantTag).filter(ParticipantTag.id == tag_id).first()
                    if tag:
                        tag_values.append(tag.name.lower().replace(" ", "_"))
                if tag_values:
                    ffv = FormFieldResponse(
                        response_id=resp.id,
                        field_id=tag_field.id,
                        value=tag_values,
                    )
                    db.add(ffv)

        db.flush()

    # ------------------------------------------------------------------ #
    # Commit all changes                                                 #
    # ------------------------------------------------------------------ #
    if not dry_run:
        db.commit()
        print("\nMigration complete! All changes committed.")
    else:
        print("\n[DRY-RUN] No changes were made.")


def main():
    parser = argparse.ArgumentParser(description="Migrate legacy RegistrationForm data to new FormDefinition system")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making any changes",
    )
    args = parser.parse_args()

    if args.dry_run:
        engine = create_engine(settings.DATABASE_URL)
        with Session(engine) as db:
            migrate(db, dry_run=True)
    else:
        db = SessionLocal()
        try:
            migrate(db, dry_run=False)
        except Exception as e:
            db.rollback()
            print(f"ERROR: Migration failed — {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            db.close()


if __name__ == "__main__":
    main()
