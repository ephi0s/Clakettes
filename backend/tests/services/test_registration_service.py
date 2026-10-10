from datetime import datetime, timezone, timedelta

from app.services.registration_service import (
    RegistrationFormService,
    RegistrationFormSectionService,
    RegistrationFormLinkService,
    FestivalRegistrationService,
)
from app.schemas.registration import (
    RegistrationFormCreate,
    RegistrationFormSectionCreate,
    RegistrationFormSectionUpdate,
    RegistrationFormLinkCreate,
    FestivalRegistrationCreate,
    FestivalRegistrationUpdate,
    SectionSelectionInput,
)
from app.models.registration import (
    RegistrationForm,
    RegistrationFormSection,
    RegistrationFormLink,
    FestivalRegistration,
    RegistrationStatus,
    RegistrationFormSectionRole,
    RegistrationFormSectionTag,
    RegistrationSectionSelection,
)
from app.models.participant_tag import ParticipantTag


class TestRegistrationFormService:
    def test_create(self, db_session, create_festival):
        festival = create_festival()
        service = RegistrationFormService()
        obj_in = RegistrationFormCreate(
            festival_id=festival.id,
            title="Test Form",
            description="Description",
        )
        result = service.create(db_session, obj_in)
        assert result.id is not None
        assert result.title == "Test Form"
        assert result.festival_id == festival.id
        assert result.is_active is True

    def test_get_by_festival(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        create_registration_form(festival_id=festival.id)
        create_registration_form(festival_id=festival.id)
        other_festival = create_festival(name="Other")
        create_registration_form(festival_id=other_festival.id)

        service = RegistrationFormService()
        results = service.get_by_festival(db_session, festival.id)
        assert len(results) == 2
        assert all(f.festival_id == festival.id for f in results)

    def test_get_by_festival_filter_active(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        create_registration_form(festival_id=festival.id, is_active=True)
        create_registration_form(festival_id=festival.id, is_active=False)

        service = RegistrationFormService()
        active = service.get_by_festival(db_session, festival.id, is_active=True)
        assert len(active) == 1
        assert active[0].is_active is True

        inactive = service.get_by_festival(db_session, festival.id, is_active=False)
        assert len(inactive) == 1
        assert inactive[0].is_active is False

    def test_create_with_sections(self, db_session, create_festival, create_role):
        festival = create_festival()
        role1 = create_role(name="role_a")
        role2 = create_role(name="role_b")
        service = RegistrationFormService()

        obj_in = RegistrationFormCreate(
            festival_id=festival.id,
            title="Form with sections",
        )
        section_data = RegistrationFormSectionCreate(
            form_id=0,
            title="Section 1",
            description="First section",
            sort_order=1,
            role_ids=[role1.id, role2.id],
            tag_ids=[],
        )
        result = service.create_with_sections(db_session, obj_in, sections=[section_data], created_by=None)
        assert result.id is not None
        assert len(result.sections) == 1
        assert result.sections[0].title == "Section 1"
        section_roles = (
            db_session.query(RegistrationFormSectionRole)
            .filter(RegistrationFormSectionRole.section_id == result.sections[0].id)
            .all()
        )
        assert len(section_roles) == 2

    def test_create_with_sections_no_sections(self, db_session, create_festival):
        festival = create_festival()
        service = RegistrationFormService()
        obj_in = RegistrationFormCreate(
            festival_id=festival.id,
            title="Form no sections",
        )
        result = service.create_with_sections(db_session, obj_in)
        assert result.id is not None
        assert len(result.sections) == 0

    def test_get_public_by_token_valid(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        service = RegistrationFormService()
        result = service.get_public_by_token(db_session, link.token)
        assert result is not None
        assert result.id == form.id

    def test_get_public_by_token_invalid_token(self, db_session):
        service = RegistrationFormService()
        result = service.get_public_by_token(db_session, "nonexistent_token")
        assert result is None

    def test_get_public_by_token_expired_form(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        past = datetime.now(timezone.utc) - timedelta(days=1)
        form = RegistrationForm(
            festival_id=festival.id,
            title="Expired Form",
            is_active=True,
            ends_at=past,
        )
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)

        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        service = RegistrationFormService()
        result = service.get_public_by_token(db_session, link.token)
        assert result is None

    def test_get_public_by_token_not_yet_started(self, db_session, create_festival):
        festival = create_festival()
        future = datetime.now(timezone.utc) + timedelta(days=1)
        form = RegistrationForm(
            festival_id=festival.id,
            title="Future Form",
            is_active=True,
            starts_at=future,
        )
        db_session.add(form)
        db_session.commit()
        db_session.refresh(form)

        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        service = RegistrationFormService()
        result = service.get_public_by_token(db_session, link.token)
        assert result is None

    def test_get_public_by_token_inactive_form(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id, is_active=False)

        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        service = RegistrationFormService()
        result = service.get_public_by_token(db_session, link.token)
        assert result is None


class TestRegistrationFormSectionService:
    def test_create_with_relations(self, db_session, create_festival, create_role):
        festival = create_festival()
        role = create_role()
        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="Test"))

        section_service = RegistrationFormSectionService()
        obj_in = RegistrationFormSectionCreate(
            form_id=form.id,
            title="My Section",
            description="Desc",
            sort_order=1,
            role_ids=[role.id],
            tag_ids=[],
        )
        result = section_service.create_with_relations(db_session, form.id, obj_in)
        assert result.id is not None
        assert result.title == "My Section"
        assert result.form_id == form.id

        roles = (
            db_session.query(RegistrationFormSectionRole)
            .filter(RegistrationFormSectionRole.section_id == result.id)
            .all()
        )
        assert len(roles) == 1
        assert roles[0].role_id == role.id

    def test_create_with_relations_with_tags(self, db_session, create_festival, create_role):
        festival = create_festival()
        role = create_role()
        tag = ParticipantTag(name="actor", display_name="Actor", category="acting")
        db_session.add(tag)
        db_session.commit()
        db_session.refresh(tag)

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="Test"))

        section_service = RegistrationFormSectionService()
        obj_in = RegistrationFormSectionCreate(
            form_id=form.id,
            title="Section with tags",
            role_ids=[role.id],
            tag_ids=[tag.id],
        )
        result = section_service.create_with_relations(db_session, form.id, obj_in)
        tags = (
            db_session.query(RegistrationFormSectionTag)
            .filter(RegistrationFormSectionTag.section_id == result.id)
            .all()
        )
        assert len(tags) == 1
        assert tags[0].tag_id == tag.id

    def test_update_with_relations(self, db_session, create_festival, create_role):
        festival = create_festival()
        role1 = create_role(name="role1")
        role2 = create_role(name="role2")

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="Test"))

        section_service = RegistrationFormSectionService()
        obj_in = RegistrationFormSectionCreate(
            form_id=form.id,
            title="Original",
            role_ids=[role1.id],
            tag_ids=[],
        )
        section = section_service.create_with_relations(db_session, form.id, obj_in)

        update_in = RegistrationFormSectionUpdate(
            title="Updated",
            role_ids=[role2.id],
        )
        updated = section_service.update_with_relations(db_session, section.id, update_in)
        assert updated.title == "Updated"

        roles = (
            db_session.query(RegistrationFormSectionRole)
            .filter(RegistrationFormSectionRole.section_id == section.id)
            .all()
        )
        assert len(roles) == 1
        assert roles[0].role_id == role2.id

    def test_update_with_relations_non_existent(self, db_session):
        section_service = RegistrationFormSectionService()
        update_in = RegistrationFormSectionUpdate(title="Nope")
        result = section_service.update_with_relations(db_session, 9999, update_in)
        assert result is None

    def test_get_by_form(self, db_session, create_festival):
        festival = create_festival()
        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="Test"))

        section_service = RegistrationFormSectionService()
        s1 = RegistrationFormSection(form_id=form.id, title="S1", sort_order=2)
        db_session.add(s1)
        s2 = RegistrationFormSection(form_id=form.id, title="S2", sort_order=1)
        db_session.add(s2)
        db_session.commit()

        results = section_service.get_by_form(db_session, form.id)
        assert len(results) == 2
        assert results[0].title == "S2"
        assert results[1].title == "S1"

    def test_get_by_form_empty(self, db_session, create_festival):
        create_festival()
        section_service = RegistrationFormSectionService()
        results = section_service.get_by_form(db_session, 9999)
        assert results == []


class TestRegistrationFormLinkService:
    def test_generate_link(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()

        obj_in = RegistrationFormLinkCreate(form_id=form.id)
        link = service.generate_link(db_session, obj_in)
        assert link.id is not None
        assert link.token is not None
        assert len(link.token) == 32
        assert link.form_id == form.id
        assert link.is_active is True
        assert link.use_count == 0

    def test_generate_link_with_params(self, db_session, create_festival, create_registration_form, create_user):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        user = create_user()
        service = RegistrationFormLinkService()

        obj_in = RegistrationFormLinkCreate(
            form_id=form.id,
            is_unique=True,
            max_uses=5,
            assigned_user_id=user.id,
            notes="Test note",
        )
        link = service.generate_link(db_session, obj_in)
        assert link.is_unique is True
        assert link.max_uses == 5
        assert link.assigned_user_id == user.id
        assert link.notes == "Test note"

    def test_consume_link_once(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        link = service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        result = service.consume_link(db_session, link.token)
        assert result is not None
        assert result.use_count == 1
        assert result.is_active is True

    def test_consume_link_unique_deactivates(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        link = service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id, is_unique=True))

        result = service.consume_link(db_session, link.token)
        assert result is not None
        assert result.use_count == 1
        assert result.is_active is False

    def test_consume_link_max_uses_reached(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        link = service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id, max_uses=2))

        result1 = service.consume_link(db_session, link.token)
        assert result1.use_count == 1
        assert result1.is_active is True

        result2 = service.consume_link(db_session, link.token)
        assert result2.use_count == 2
        assert result2.is_active is False

    def test_consume_link_expired(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        link = service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id, expires_at=past))

        result = service.consume_link(db_session, link.token)
        assert result is None

    def test_consume_link_invalid_token(self, db_session):
        service = RegistrationFormLinkService()
        result = service.consume_link(db_session, "bad_token")
        assert result is None

    def test_get_by_form(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        other_festival = create_festival(name="Other")
        other_form = create_registration_form(festival_id=other_festival.id)
        service.generate_link(db_session, RegistrationFormLinkCreate(form_id=other_form.id))

        results = service.get_by_form(db_session, form.id)
        assert len(results) == 2

    def test_get_by_form_filter_active(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        link2 = service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        db_session.query(RegistrationFormLink).filter(RegistrationFormLink.id == link2.id).update({"is_active": False})
        db_session.commit()

        active = service.get_by_form(db_session, form.id, is_active=True)
        assert len(active) == 1
        assert active[0].is_active is True

        inactive = service.get_by_form(db_session, form.id, is_active=False)
        assert len(inactive) == 1
        assert inactive[0].is_active is False

    def test_get_by_form_paginated(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        for _ in range(5):
            service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        page1 = service.get_by_form_paginated(db_session, form.id, page=1, size=2)
        assert page1["total"] == 5
        assert len(page1["items"]) == 2
        assert page1["page"] == 1
        assert page1["pages"] == 3

        page3 = service.get_by_form_paginated(db_session, form.id, page=3, size=2)
        assert len(page3["items"]) == 1

    def test_get_by_form_paginated_filter_active(self, db_session, create_festival, create_registration_form):
        festival = create_festival()
        form = create_registration_form(festival_id=festival.id)
        service = RegistrationFormLinkService()
        service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        link2 = service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        db_session.query(RegistrationFormLink).filter(RegistrationFormLink.id == link2.id).update({"is_active": False})
        db_session.commit()

        result = service.get_by_form_paginated(db_session, form.id, page=1, size=10, is_active=True)
        assert result["total"] == 1


class TestFestivalRegistrationService:
    def test_register_user_success(self, db_session, create_festival, create_user, create_role):
        festival = create_festival()
        user = create_user()
        role = create_role()

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="Reg Form"))

        section_service = RegistrationFormSectionService()
        section = section_service.create_with_relations(
            db_session,
            form.id,
            RegistrationFormSectionCreate(
                form_id=form.id,
                title="Section 1",
                role_ids=[role.id],
                tag_ids=[],
            ),
        )

        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        reg_service = FestivalRegistrationService()
        reg_in = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link.token,
            sections=[SectionSelectionInput(section_id=section.id, role_id=role.id)],
        )
        reg = reg_service.register_user(db_session, user.id, reg_in)
        assert reg is not None
        assert reg.user_id == user.id
        assert reg.festival_id == festival.id
        assert reg.form_id == form.id
        assert reg.link_id == link.id
        assert reg.status == RegistrationStatus.PENDING

        selections = (
            db_session.query(RegistrationSectionSelection)
            .filter(RegistrationSectionSelection.registration_id == reg.id)
            .all()
        )
        assert len(selections) == 1
        assert selections[0].role_id == role.id

    def test_register_user_invalid_link(self, db_session, create_user):
        user = create_user()
        reg_service = FestivalRegistrationService()
        reg_in = FestivalRegistrationCreate(
            form_id=1,
            link_token="bad_token",
            sections=[],
        )
        result = reg_service.register_user(db_session, user.id, reg_in)
        assert result is None

    def test_register_user_inactive_form(self, db_session, create_festival, create_user, create_registration_form):
        festival = create_festival()
        user = create_user()
        form = create_registration_form(festival_id=festival.id, is_active=False)

        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        reg_service = FestivalRegistrationService()
        reg_in = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link.token,
            sections=[],
        )
        result = reg_service.register_user(db_session, user.id, reg_in)
        assert result is None

    def test_register_user_max_registrations_reached(self, db_session, create_festival, create_user, create_role):
        festival = create_festival()
        user = create_user()
        role = create_role()

        form_service = RegistrationFormService()
        form = form_service.create(
            db_session, RegistrationFormCreate(festival_id=festival.id, title="Limited Form", max_registrations=1)
        )

        section_service = RegistrationFormSectionService()
        section = section_service.create_with_relations(
            db_session,
            form.id,
            RegistrationFormSectionCreate(
                form_id=form.id,
                title="S1",
                role_ids=[role.id],
                tag_ids=[],
            ),
        )

        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))

        reg_service = FestivalRegistrationService()
        reg_in = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link.token,
            sections=[SectionSelectionInput(section_id=section.id, role_id=role.id)],
        )
        first = reg_service.register_user(db_session, user.id, reg_in)
        assert first is not None

        other_user = create_user(username="other", email="other@test.com")
        link2 = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_in2 = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link2.token,
            sections=[SectionSelectionInput(section_id=section.id, role_id=role.id)],
        )
        second = reg_service.register_user(db_session, other_user.id, reg_in2)
        assert second is None

    def test_register_user_unique_link_wrong_user(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()
        other_user = create_user(username="other", email="other@test.com")

        form_service = RegistrationFormService()
        form = form_service.create(
            db_session, RegistrationFormCreate(festival_id=festival.id, title="Unique Link Form")
        )

        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(
            db_session,
            RegistrationFormLinkCreate(
                form_id=form.id,
                is_unique=True,
                assigned_user_id=other_user.id,
            ),
        )

        reg_service = FestivalRegistrationService()
        reg_in = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link.token,
            sections=[],
        )
        result = reg_service.register_user(db_session, user.id, reg_in)
        assert result is None

    def test_get_by_festival(self, db_session, create_festival, create_user, create_role):
        festival = create_festival()
        user = create_user()
        role = create_role()

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        section_service = RegistrationFormSectionService()
        section = section_service.create_with_relations(
            db_session,
            form.id,
            RegistrationFormSectionCreate(
                form_id=form.id,
                title="S",
                role_ids=[role.id],
                tag_ids=[],
            ),
        )
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg_in = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link.token,
            sections=[SectionSelectionInput(section_id=section.id, role_id=role.id)],
        )
        reg_service.register_user(db_session, user.id, reg_in)

        results = reg_service.get_by_festival(db_session, festival.id)
        assert len(results) == 1
        assert results[0].festival_id == festival.id

    def test_get_by_festival_excludes_hidden(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg_in = FestivalRegistrationCreate(form_id=form.id, link_token=link.token, sections=[])
        reg_service.register_user(db_session, user.id, reg_in)

        reg = db_session.query(FestivalRegistration).first()
        reg.is_hidden = True
        db_session.commit()

        results = reg_service.get_by_festival(db_session, festival.id)
        assert len(results) == 0

        results_with_hidden = reg_service.get_by_festival(db_session, festival.id, include_hidden=True)
        assert len(results_with_hidden) == 1

    def test_get_by_festival_filter_status(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=festival.id,
            form_id=form.id,
            link_id=link.id,
            status=RegistrationStatus.APPROVED.value,
        )
        db_session.add(reg)
        db_session.commit()

        pending = reg_service.get_by_festival(db_session, festival.id, status=RegistrationStatus.PENDING.value)
        assert len(pending) == 0

        approved = reg_service.get_by_festival(db_session, festival.id, status=RegistrationStatus.APPROVED.value)
        assert len(approved) == 1

    def test_get_by_festival_paginated(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        reg_service = FestivalRegistrationService()

        for _ in range(5):
            link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
            reg = FestivalRegistration(
                user_id=user.id,
                festival_id=festival.id,
                form_id=form.id,
                link_id=link.id,
                status=RegistrationStatus.PENDING.value,
            )
            db_session.add(reg)
        db_session.commit()

        result = reg_service.get_by_festival_paginated(db_session, festival.id, page=1, size=2)
        assert result["total"] == 5
        assert len(result["items"]) == 2

    def test_get_by_user(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg1 = FestivalRegistration(
            user_id=user.id,
            festival_id=festival.id,
            form_id=form.id,
            link_id=link.id,
            status=RegistrationStatus.PENDING.value,
        )
        db_session.add(reg1)
        db_session.commit()

        results = reg_service.get_by_user(db_session, user.id)
        assert len(results) == 1
        assert results[0].user_id == user.id

    def test_approve_registration(self, db_session, create_festival, create_user, create_role):
        festival = create_festival()
        user = create_user()
        admin = create_user(username="admin", email="admin@test.com")
        role = create_role()

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        section_service = RegistrationFormSectionService()
        section = section_service.create_with_relations(
            db_session,
            form.id,
            RegistrationFormSectionCreate(
                form_id=form.id,
                title="S",
                role_ids=[role.id],
                tag_ids=[],
            ),
        )
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg_in = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link.token,
            sections=[SectionSelectionInput(section_id=section.id, role_id=role.id)],
        )
        reg = reg_service.register_user(db_session, user.id, reg_in)

        approved = reg_service.approve_registration(db_session, reg.id, admin.id)
        assert approved is not None
        assert approved.status == RegistrationStatus.APPROVED
        assert approved.approved_by == admin.id

        from app.models.user_role import UserRole

        user_role = (
            db_session.query(UserRole)
            .filter(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id,
                UserRole.festival_id == festival.id,
            )
            .first()
        )
        assert user_role is not None
        from app.models.user_role import UserRoleStatus

        assert user_role.status == UserRoleStatus.APPROVED

    def test_approve_registration_with_tags(self, db_session, create_festival, create_user, create_role):
        festival = create_festival()
        user = create_user()
        admin = create_user(username="admin", email="admin@test.com")
        role = create_role()

        tag = ParticipantTag(name="actor", display_name="Actor", category="acting")
        db_session.add(tag)
        db_session.commit()
        db_session.refresh(tag)

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        section_service = RegistrationFormSectionService()
        section = section_service.create_with_relations(
            db_session,
            form.id,
            RegistrationFormSectionCreate(
                form_id=form.id,
                title="S",
                role_ids=[role.id],
                tag_ids=[tag.id],
            ),
        )
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg_in = FestivalRegistrationCreate(
            form_id=form.id,
            link_token=link.token,
            sections=[SectionSelectionInput(section_id=section.id, role_id=role.id, additional_tag_ids=[tag.id])],
        )
        reg = reg_service.register_user(db_session, user.id, reg_in)

        approved = reg_service.approve_registration(db_session, reg.id, admin.id)
        assert approved.status == RegistrationStatus.APPROVED

        from app.models.user_role import UserParticipantTag

        upt = (
            db_session.query(UserParticipantTag)
            .filter(
                UserParticipantTag.user_id == user.id,
                UserParticipantTag.tag_id == tag.id,
                UserParticipantTag.festival_id == festival.id,
            )
            .first()
        )
        assert upt is not None
        assert upt.is_primary is True

    def test_approve_registration_non_pending(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()
        admin = create_user(username="admin", email="admin@test.com")

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=festival.id,
            form_id=form.id,
            link_id=link.id,
            status=RegistrationStatus.REJECTED.value,
        )
        db_session.add(reg)
        db_session.commit()
        db_session.refresh(reg)

        result = reg_service.approve_registration(db_session, reg.id, admin.id)
        assert result is None

    def test_reject_registration(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()
        admin = create_user(username="admin", email="admin@test.com")

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg_in = FestivalRegistrationCreate(form_id=form.id, link_token=link.token, sections=[])
        reg = reg_service.register_user(db_session, user.id, reg_in)

        rejected = reg_service.reject_registration(db_session, reg.id, admin.id, reason="Not eligible")
        assert rejected is not None
        assert rejected.status == RegistrationStatus.REJECTED
        assert rejected.approved_by == admin.id
        assert "Not eligible" in rejected.notes

    def test_reject_registration_non_pending(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()
        admin = create_user(username="admin", email="admin@test.com")

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg = FestivalRegistration(
            user_id=user.id,
            festival_id=festival.id,
            form_id=form.id,
            link_id=link.id,
            status=RegistrationStatus.APPROVED.value,
        )
        db_session.add(reg)
        db_session.commit()
        db_session.refresh(reg)

        result = reg_service.reject_registration(db_session, reg.id, admin.id)
        assert result is None

    def test_reject_registration_nonexistent(self, db_session):
        reg_service = FestivalRegistrationService()
        result = reg_service.reject_registration(db_session, 9999, 1)
        assert result is None

    def test_modify_registration(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()
        admin = create_user(username="admin", email="admin@test.com")

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        reg_service = FestivalRegistrationService()

        reg_in = FestivalRegistrationCreate(form_id=form.id, link_token=link.token, sections=[])
        reg = reg_service.register_user(db_session, user.id, reg_in)

        update_in = FestivalRegistrationUpdate(notes="Updated notes", is_hidden=True)
        modified = reg_service.modify_registration(db_session, reg.id, update_in, admin.id)
        assert modified is not None
        assert modified.notes == "Updated notes"
        assert modified.is_hidden is True
        assert modified.assigned_by == admin.id

    def test_modify_registration_nonexistent(self, db_session):
        reg_service = FestivalRegistrationService()
        update_in = FestivalRegistrationUpdate(notes="Nope")
        result = reg_service.modify_registration(db_session, 9999, update_in, 1)
        assert result is None

    def test_get_user_registrations_in_festival(self, db_session, create_festival, create_user):
        festival = create_festival()
        user = create_user()
        other_festival = create_festival(name="Other")

        form_service = RegistrationFormService()
        form = form_service.create(db_session, RegistrationFormCreate(festival_id=festival.id, title="F"))
        other_form = form_service.create(db_session, RegistrationFormCreate(festival_id=other_festival.id, title="OF"))
        link_service = RegistrationFormLinkService()
        link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=form.id))
        other_link = link_service.generate_link(db_session, RegistrationFormLinkCreate(form_id=other_form.id))
        reg_service = FestivalRegistrationService()

        reg1 = FestivalRegistration(
            user_id=user.id,
            festival_id=festival.id,
            form_id=form.id,
            link_id=link.id,
            status=RegistrationStatus.PENDING.value,
        )
        reg2 = FestivalRegistration(
            user_id=user.id,
            festival_id=other_festival.id,
            form_id=other_form.id,
            link_id=other_link.id,
            status=RegistrationStatus.PENDING.value,
        )
        db_session.add_all([reg1, reg2])
        db_session.commit()

        results = reg_service.get_user_registrations_in_festival(db_session, user.id, festival.id)
        assert len(results) == 1
        assert results[0].festival_id == festival.id
