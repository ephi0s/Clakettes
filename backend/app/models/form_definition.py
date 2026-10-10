"""Form definition models — dynamic form system replacing registration forms."""

import uuid

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import FormType, FormFieldType, FormAccessLevel, SubmissionStatus


class FormDefinition(BaseModel):
    __tablename__ = "form_definitions"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    form_type = Column(SQLEnum(FormType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    max_submissions = Column(Integer, nullable=True)
    require_auth = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)
    success_message = Column(Text, nullable=True)
    submit_button_text = Column(String(100), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    settings = Column(JSON, nullable=True)
    sort_order = Column(Integer, default=0)

    festival = relationship("Festival", backref="form_definitions", foreign_keys=[festival_id])
    creator = relationship("User", backref="created_forms", foreign_keys=[created_by])
    pages = relationship("FormPage", back_populates="form", cascade="all, delete-orphan")
    links = relationship("FormLink", back_populates="form", cascade="all, delete-orphan")
    responses = relationship("FormResponse", back_populates="form")
    access_rules = relationship("FormAccessRule", back_populates="form", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FormDefinition(id={self.id}, title='{self.title}', type='{self.form_type.value}')>"


class FormPage(BaseModel):
    __tablename__ = "form_pages"

    form_id = Column(Integer, ForeignKey("form_definitions.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    is_repeatable = Column(Boolean, default=False)

    form = relationship("FormDefinition", back_populates="pages")
    fields = relationship("FormField", back_populates="page", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FormPage(id={self.id}, title='{self.title}', order={self.sort_order})>"


class FormField(BaseModel):
    __tablename__ = "form_fields"

    page_id = Column(Integer, ForeignKey("form_pages.id"), nullable=False, index=True)
    field_type = Column(SQLEnum(FormFieldType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    label = Column(String(200), nullable=False)
    help_text = Column(Text, nullable=True)
    placeholder = Column(String(200), nullable=True)
    is_required = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    is_read_only = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    default_value = Column(Text, nullable=True)
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)
    min_value = Column(Integer, nullable=True)
    max_value = Column(Integer, nullable=True)
    regex_pattern = Column(String(500), nullable=True)
    error_message = Column(String(500), nullable=True)
    allowed_values = Column(JSON, nullable=True)
    depends_on_field_id = Column(Integer, ForeignKey("form_fields.id"), nullable=True)
    depends_on_value = Column(String(500), nullable=True)
    role_filter = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    width_class = Column(String(20), nullable=True)

    page = relationship("FormPage", back_populates="fields")
    options = relationship("FormFieldOption", back_populates="field", cascade="all, delete-orphan")
    dependent_fields = relationship("FormField", backref="depends_on_field", remote_side="FormField.id")
    responses = relationship("FormFieldResponse", back_populates="field")

    def __repr__(self):
        return f"<FormField(id={self.id}, label='{self.label}', type='{self.field_type.value}')>"


class FormFieldOption(BaseModel):
    __tablename__ = "form_field_options"

    field_id = Column(Integer, ForeignKey("form_fields.id"), nullable=False, index=True)
    value = Column(String(200), nullable=False)
    label = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)

    field = relationship("FormField", back_populates="options")

    def __repr__(self):
        return f"<FormFieldOption(id={self.id}, value='{self.value}')>"


class FormResponse(BaseModel):
    __tablename__ = "form_responses"

    form_id = Column(Integer, ForeignKey("form_definitions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    status = Column(
        SQLEnum(SubmissionStatus, values_callable=lambda x: [e.value for e in x]),
        default=SubmissionStatus.DRAFT,
        nullable=False,
    )
    submitted_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    link_token = Column(String(64), nullable=True)

    form = relationship("FormDefinition", back_populates="responses")
    user = relationship("User", foreign_keys=[user_id], backref="form_responses")
    festival = relationship("Festival", foreign_keys=[festival_id], backref="form_responses")
    reviewer = relationship("User", foreign_keys=[reviewer_id], backref="reviewed_responses")
    field_responses = relationship("FormFieldResponse", back_populates="response", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FormResponse(id={self.id}, status='{self.status.value}')>"


class FormFieldResponse(BaseModel):
    __tablename__ = "form_field_responses"

    response_id = Column(Integer, ForeignKey("form_responses.id"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("form_fields.id"), nullable=False)
    value = Column(JSON, nullable=True)
    file_url = Column(String(500), nullable=True)

    response = relationship("FormResponse", back_populates="field_responses")
    field = relationship("FormField", back_populates="responses")

    def __repr__(self):
        return f"<FormFieldResponse(response_id={self.response_id}, field_id={self.field_id})>"


class FormAccessRule(BaseModel):
    __tablename__ = "form_access_rules"

    form_id = Column(Integer, ForeignKey("form_definitions.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    access_level = Column(SQLEnum(FormAccessLevel, values_callable=lambda x: [e.value for e in x]), nullable=False)
    is_deny = Column(Boolean, default=False)

    form = relationship("FormDefinition", back_populates="access_rules")
    role = relationship("Role", backref="form_access_rules")

    def __repr__(self):
        return f"<FormAccessRule(form_id={self.form_id}, level='{self.access_level.value}', deny={self.is_deny})>"


class FormLink(BaseModel):
    __tablename__ = "form_links"

    form_id = Column(Integer, ForeignKey("form_definitions.id"), nullable=False, index=True)
    token = Column(String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex, index=True)
    is_unique = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    use_count = Column(Integer, default=0)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    form = relationship("FormDefinition", back_populates="links")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    responses = relationship(
        "FormResponse",
        backref="link",
        primaryjoin="FormLink.token == FormResponse.link_token",
        foreign_keys="FormResponse.link_token",
    )

    def __repr__(self):
        return f"<FormLink(token='{self.token[:8]}...', unique={self.is_unique})>"
