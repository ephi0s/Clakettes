from pydantic import BaseModel, ConfigDict
from typing import Any, Optional
from datetime import datetime
from .common import PageBase
from app.enums import FormType, FormFieldType, FormAccessLevel, SubmissionStatus


class FormDefinitionBase(BaseModel):
    title: str
    description: str | None = None
    form_type: FormType
    festival_id: int | None = None
    is_active: bool = True
    is_public: bool = False
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    max_submissions: int | None = None
    require_auth: bool = True
    requires_approval: bool = True
    success_message: str | None = None
    submit_button_text: str | None = None
    created_by: int | None = None
    settings: dict[str, Any] | None = None
    sort_order: int = 0


class FormDefinitionCreate(FormDefinitionBase):
    pages: list[Optional["FormPageCreate"]] = None


class FormDefinitionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    form_type: FormType | None = None
    festival_id: int | None = None
    is_active: bool | None = None
    is_public: bool | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    max_submissions: int | None = None
    require_auth: bool | None = None
    requires_approval: bool | None = None
    success_message: str | None = None
    submit_button_text: str | None = None
    settings: dict[str, Any] | None = None
    sort_order: int | None = None


class FormDefinitionResponse(FormDefinitionBase):
    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime
    pages: list["FormPageResponse"] = []
    links: list["FormLinkResponse"] = []
    access_rules: list["FormAccessRuleResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class FormDefinitionPublicResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    form_type: FormType
    festival_id: int | None = None
    is_public: bool
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    require_auth: bool
    success_message: str | None = None
    submit_button_text: str | None = None
    pages: list["FormPageResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class FormPageBase(BaseModel):
    form_id: int
    title: str
    description: str | None = None
    sort_order: int = 0
    is_repeatable: bool = False


class FormPageCreate(BaseModel):
    title: str
    description: str | None = None
    sort_order: int = 0
    is_repeatable: bool = False
    fields: list[Optional["FormFieldCreate"]] = None


class FormPageUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    sort_order: int | None = None
    is_repeatable: bool | None = None


class FormPageResponse(BaseModel):
    id: int
    form_id: int
    title: str
    description: str | None = None
    sort_order: int
    is_repeatable: bool
    created_at: datetime
    updated_at: datetime
    fields: list["FormFieldResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class FormFieldBase(BaseModel):
    page_id: int = 0
    field_type: FormFieldType
    label: str
    help_text: str | None = None
    placeholder: str | None = None
    is_required: bool = False
    is_visible: bool = True
    is_read_only: bool = False
    sort_order: int = 0
    default_value: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_value: int | None = None
    max_value: int | None = None
    regex_pattern: str | None = None
    error_message: str | None = None
    allowed_values: list[str] | None = None
    depends_on_field_id: int | None = None
    depends_on_value: str | None = None
    role_filter: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    width_class: str | None = None


class FormFieldCreate(FormFieldBase):
    options: list[Optional["FormFieldOptionCreate"]] = None


class FormFieldUpdate(BaseModel):
    page_id: int | None = None
    field_type: FormFieldType | None = None
    label: str | None = None
    help_text: str | None = None
    placeholder: str | None = None
    is_required: bool | None = None
    is_visible: bool | None = None
    is_read_only: bool | None = None
    sort_order: int | None = None
    default_value: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_value: int | None = None
    max_value: int | None = None
    regex_pattern: str | None = None
    error_message: str | None = None
    allowed_values: list[str] | None = None
    depends_on_field_id: int | None = None
    depends_on_value: str | None = None
    role_filter: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    width_class: str | None = None


class FormFieldResponse(BaseModel):
    id: int
    page_id: int
    field_type: FormFieldType
    label: str
    help_text: str | None = None
    placeholder: str | None = None
    is_required: bool
    is_visible: bool
    is_read_only: bool
    sort_order: int
    default_value: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_value: int | None = None
    max_value: int | None = None
    regex_pattern: str | None = None
    error_message: str | None = None
    allowed_values: list[str] | None = None
    depends_on_field_id: int | None = None
    depends_on_value: str | None = None
    role_filter: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    width_class: str | None = None
    created_at: datetime
    updated_at: datetime
    options: list["FormFieldOptionResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class FormFieldOptionBase(BaseModel):
    field_id: int
    value: str
    label: str
    sort_order: int = 0


class FormFieldOptionCreate(BaseModel):
    value: str
    label: str
    sort_order: int = 0


class FormFieldOptionResponse(BaseModel):
    id: int
    field_id: int
    value: str
    label: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FormResponseBase(BaseModel):
    form_id: int
    user_id: int | None = None
    festival_id: int | None = None
    status: SubmissionStatus = SubmissionStatus.DRAFT
    link_token: str | None = None


class FormResponseCreate(BaseModel):
    field_values: dict[str, Any] = {}


class FormResponseUpdate(BaseModel):
    status: SubmissionStatus | None = None
    review_notes: str | None = None


class FormResponseResponse(BaseModel):
    id: int
    form_id: int
    user_id: int | None = None
    festival_id: int | None = None
    status: SubmissionStatus
    submitted_at: datetime | None = None
    reviewer_id: int | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    link_token: str | None = None
    created_at: datetime
    updated_at: datetime
    field_responses: list["FormFieldResponseResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class FormFieldResponseBase(BaseModel):
    response_id: int
    field_id: int
    value: Any | None = None
    file_url: str | None = None


class FormFieldResponseResponse(BaseModel):
    id: int
    response_id: int
    field_id: int
    value: Any | None = None
    file_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FormAccessRuleBase(BaseModel):
    form_id: int
    role_id: int | None = None
    access_level: FormAccessLevel
    is_deny: bool = False


class FormAccessRuleCreate(BaseModel):
    role_id: int | None = None
    access_level: FormAccessLevel
    is_deny: bool = False


class FormAccessRuleResponse(BaseModel):
    id: int
    form_id: int
    role_id: int | None = None
    access_level: FormAccessLevel
    is_deny: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FormLinkBase(BaseModel):
    form_id: int
    token: str
    is_unique: bool = False
    is_public: bool = True
    is_active: bool = True
    expires_at: datetime | None = None
    max_uses: int | None = None
    assigned_user_id: int | None = None
    notes: str | None = None


class FormLinkCreate(BaseModel):
    is_unique: bool = False
    is_public: bool = True
    expires_at: datetime | None = None
    max_uses: int | None = None
    assigned_user_id: int | None = None
    notes: str | None = None


class FormLinkResponse(BaseModel):
    id: int
    form_id: int
    token: str
    is_unique: bool
    is_public: bool
    is_active: bool
    expires_at: datetime | None = None
    max_uses: int | None = None
    use_count: int
    assigned_user_id: int | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FormCloneRequest(BaseModel):
    title: str | None = None


class FormDefinitionPage(PageBase):
    items: list[FormDefinitionResponse]


class FormResponsePage(PageBase):
    items: list[FormResponseResponse]


class FormLinkPage(PageBase):
    items: list[FormLinkResponse]


# Forward references

FormDefinitionResponse.model_rebuild()
FormDefinitionPublicResponse.model_rebuild()
FormPageResponse.model_rebuild()
FormFieldResponse.model_rebuild()
FormResponseResponse.model_rebuild()
FormDefinitionCreate.model_rebuild()
FormPageCreate.model_rebuild()
FormFieldCreate.model_rebuild()
FormFieldBase.model_rebuild()
