"""Registration models — inscription forms, links, and user registrations for festivals."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import PaymentStatus, RegistrationStatus


class RegistrationForm(BaseModel):
    """Form that festival organizers create for people to register into festival roles.

    Each form is tied to a festival and can have multiple sections (each with
    specific roles and tags). Access is through registration links.
    """

    __tablename__ = "registration_forms"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    max_registrations = Column(Integer, nullable=True)
    require_existing_account = Column(Boolean, default=True)
    allow_role_selection = Column(Boolean, default=True)
    allow_tag_selection = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    fee_amount = Column(Float, nullable=True, default=None)
    currency = Column(String(3), default="EUR", nullable=False)

    festival = relationship("Festival", back_populates="registration_forms")
    sections = relationship("RegistrationFormSection", back_populates="form", cascade="all, delete-orphan")
    links = relationship("RegistrationFormLink", back_populates="form", cascade="all, delete-orphan")
    registrations = relationship("FestivalRegistration", back_populates="form")

    def __repr__(self):
        return f"<RegistrationForm(id={self.id}, title='{self.title}', festival_id={self.festival_id})>"


class RegistrationFormSection(BaseModel):
    """A section within a registration form, grouping specific roles and tags.

    Example: "Staff Section" with roles like programmer, technician, volunteer.
    Users can select their desired role and any applicable tags within a section.
    """

    __tablename__ = "registration_form_sections"

    form_id = Column(Integer, ForeignKey("registration_forms.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    allow_multiple_roles = Column(Boolean, default=False)
    max_selections = Column(Integer, nullable=True)
    is_required = Column(Boolean, default=True)

    form = relationship("RegistrationForm", back_populates="sections")
    role_assignments = relationship(
        "RegistrationFormSectionRole", back_populates="section", cascade="all, delete-orphan"
    )
    tag_assignments = relationship("RegistrationFormSectionTag", back_populates="section", cascade="all, delete-orphan")
    user_selections = relationship("RegistrationSectionSelection", back_populates="section")

    def __repr__(self):
        return f"<RegistrationFormSection(id={self.id}, title='{self.title}')>"


class RegistrationFormSectionRole(BaseModel):
    """Links a registration form section to specific roles."""

    __tablename__ = "registration_form_section_roles"

    section_id = Column(Integer, ForeignKey("registration_form_sections.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    max_assignees = Column(Integer, nullable=True)
    requires_approval = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    section = relationship("RegistrationFormSection", back_populates="role_assignments")
    role = relationship("Role")

    def __repr__(self):
        return f"<RegistrationFormSectionRole(section_id={self.section_id}, role_id={self.role_id})>"


class RegistrationFormSectionTag(BaseModel):
    """Links a registration form section to specific participant tags."""

    __tablename__ = "registration_form_section_tags"

    section_id = Column(Integer, ForeignKey("registration_form_sections.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("participant_tags.id"), nullable=False)
    is_required = Column(Boolean, default=False)
    max_selections = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0)

    section = relationship("RegistrationFormSection", back_populates="tag_assignments")
    tag = relationship("ParticipantTag")

    def __repr__(self):
        return f"<RegistrationFormSectionTag(section_id={self.section_id}, tag_id={self.tag_id})>"


class RegistrationFormLink(BaseModel):
    """Link to access a registration form — can be unique or public.

    Unique links: single-use, pre-assigned to a specific user, random token.
    Public links: reusable, accessible by anyone who has the token.
    """

    __tablename__ = "registration_form_links"

    form_id = Column(Integer, ForeignKey("registration_forms.id"), nullable=False, index=True)
    token = Column(String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex, index=True)
    is_unique = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    use_count = Column(Integer, default=0)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    form = relationship("RegistrationForm", back_populates="links")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    registrations = relationship("FestivalRegistration", back_populates="link")

    def __repr__(self):
        return f"<RegistrationFormLink(token='{self.token[:8]}...', unique={self.is_unique})>"


class FestivalRegistration(BaseModel):
    """A user's registration for a festival through a registration form.

    Tracks the entire lifecycle: from application through approval/rejection.
    Upper hierarchy can modify any registration they manage.
    """

    __tablename__ = "festival_registrations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    form_id = Column(Integer, ForeignKey("registration_forms.id"), nullable=True)
    link_id = Column(Integer, ForeignKey("registration_form_links.id"), nullable=True)
    status = Column(
        SQLEnum(RegistrationStatus, values_callable=lambda x: [e.value for e in x]),
        default=RegistrationStatus.PENDING,
        nullable=False,
    )
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    is_hidden = Column(Boolean, default=False)
    payment_status = Column(String(20), default=PaymentStatus.UNPAID.value, nullable=False, index=True)
    paid_at = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="festival_registrations")
    festival = relationship("Festival", foreign_keys=[festival_id], back_populates="registrations")
    form = relationship("RegistrationForm", back_populates="registrations")
    link = relationship("RegistrationFormLink", back_populates="registrations")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by], back_populates="assigned_registrations")
    approved_by_user = relationship("User", foreign_keys=[approved_by], back_populates="approved_registrations")
    selections = relationship(
        "RegistrationSectionSelection", back_populates="registration", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<FestivalRegistration(user_id={self.user_id}, "
            f"festival_id={self.festival_id}, status={self.status.value})>"
        )


class RegistrationSectionSelection(BaseModel):
    """User's selection within a registration form section (roles + tags chosen)."""

    __tablename__ = "registration_section_selections"

    registration_id = Column(Integer, ForeignKey("festival_registrations.id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("registration_form_sections.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    additional_tags = Column(JSON, nullable=True)  # JSON list of selected tag IDs
    notes = Column(Text, nullable=True)

    registration = relationship("FestivalRegistration", back_populates="selections")
    section = relationship("RegistrationFormSection", back_populates="user_selections")
    role = relationship("Role")

    def __repr__(self):
        return f"<RegistrationSectionSelection(registration_id={self.registration_id}, section_id={self.section_id})>"
