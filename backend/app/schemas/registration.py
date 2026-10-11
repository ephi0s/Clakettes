from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from .common import PageBase
from app.enums import RegistrationStatus


class RegistrationFormBase(BaseModel):
    festival_id: int
    title: str
    description: str | None = None
    is_active: bool = True
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    max_registrations: int | None = None
    require_existing_account: bool = True
    allow_role_selection: bool = True
    allow_tag_selection: bool = True
    fee_amount: float | None = Field(default=None, ge=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)


class RegistrationFormCreate(RegistrationFormBase):
    pass


class RegistrationFormUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    max_registrations: int | None = None
    require_existing_account: bool | None = None
    allow_role_selection: bool | None = None
    allow_tag_selection: bool | None = None
    fee_amount: float | None = Field(default=None, ge=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)


class RegistrationFormResponse(RegistrationFormBase):
    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime
    sections: list["RegistrationFormSectionResponse"] = []
    links: list["RegistrationFormLinkResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class RegistrationFormPublicResponse(BaseModel):
    """Public response for registration forms — no internal data."""

    id: int
    title: str
    description: str | None = None
    festival_id: int
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    require_existing_account: bool
    fee_amount: float | None = None
    currency: str = "EUR"
    sections: list["RegistrationFormSectionResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class RegistrationFormSectionBase(BaseModel):
    form_id: int
    title: str
    description: str | None = None
    sort_order: int = 0
    allow_multiple_roles: bool = False
    max_selections: int | None = None
    is_required: bool = True


class RegistrationFormSectionCreate(RegistrationFormSectionBase):
    role_ids: list[int] = []
    tag_ids: list[int] = []


class RegistrationFormSectionInput(BaseModel):
    """Section payload for form creation (form_id is assigned server-side)."""

    title: str
    description: str | None = None
    sort_order: int = 0
    allow_multiple_roles: bool = False
    max_selections: int | None = None
    is_required: bool = True
    role_ids: list[int] = []
    tag_ids: list[int] = []


class RegistrationFormCreateWithSections(RegistrationFormCreate):
    festival_id: int | None = None
    sections: list[RegistrationFormSectionInput] = []


class RegistrationFormSectionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    sort_order: int | None = None
    allow_multiple_roles: bool | None = None
    max_selections: int | None = None
    is_required: bool | None = None
    role_ids: list[int] | None = None
    tag_ids: list[int] | None = None


class RegistrationFormSectionRoleResponse(BaseModel):
    id: int
    section_id: int
    role_id: int
    max_assignees: int | None = None
    requires_approval: bool = False
    sort_order: int = 0
    role: Optional["RoleResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationFormSectionTagResponse(BaseModel):
    id: int
    section_id: int
    tag_id: int
    is_required: bool = False
    max_selections: int | None = None
    sort_order: int = 0
    tag: Optional["ParticipantTagResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationFormSectionResponse(BaseModel):
    id: int
    form_id: int
    title: str
    description: str | None = None
    sort_order: int
    allow_multiple_roles: bool
    max_selections: int | None = None
    is_required: bool
    created_at: datetime
    updated_at: datetime
    role_assignments: list[RegistrationFormSectionRoleResponse] = []
    tag_assignments: list[RegistrationFormSectionTagResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RegistrationFormLinkBase(BaseModel):
    form_id: int
    token: str
    is_unique: bool = False
    is_public: bool = True
    is_active: bool = True
    expires_at: datetime | None = None
    max_uses: int | None = None
    assigned_user_id: int | None = None
    notes: str | None = None


class RegistrationFormLinkCreate(BaseModel):
    form_id: int | None = None
    is_unique: bool = False
    is_public: bool = True
    expires_at: datetime | None = None
    max_uses: int | None = None
    assigned_user_id: int | None = None
    notes: str | None = None


class RegistrationFormLinkResponse(BaseModel):
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


class FestivalRegistrationBase(BaseModel):
    user_id: int
    festival_id: int
    form_id: int | None = None
    link_id: int | None = None
    status: str = RegistrationStatus.PENDING.value
    notes: str | None = None
    is_hidden: bool = False


class SectionSelectionInput(BaseModel):
    section_id: int
    role_id: int | None = None
    additional_tag_ids: list[int] = []


class FestivalRegistrationCreate(BaseModel):
    form_id: int
    link_token: str
    sections: list[SectionSelectionInput] = []


class FestivalRegistrationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    is_hidden: bool | None = None


class PaymentUpdate(BaseModel):
    """Manual/offline payment details for marking a registration as paid."""

    method: str | None = None
    transaction_id: str | None = None


class FestivalRegistrationResponse(BaseModel):
    id: int
    user_id: int
    festival_id: int
    form_id: int | None = None
    link_id: int | None = None
    status: str
    assigned_by: int | None = None
    approved_by: int | None = None
    approved_at: datetime | None = None
    notes: str | None = None
    is_hidden: bool
    payment_status: str
    paid_at: datetime | None = None
    payment_method: str | None = None
    transaction_id: str | None = None
    created_at: datetime
    updated_at: datetime
    selections: list["RegistrationSectionSelectionResponse"] = []
    user: Optional["UserResponse"] = None
    festival: Optional["FestivalResponse"] = None
    form: RegistrationFormResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationSectionSelectionResponse(BaseModel):
    id: int
    registration_id: int
    section_id: int
    role_id: int | None = None
    additional_tags: list[int] | None = None
    notes: str | None = None
    section: RegistrationFormSectionResponse | None = None
    role: Optional["RoleResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationFormPage(PageBase):
    items: list[RegistrationFormResponse]


class FestivalRegistrationPage(PageBase):
    items: list[FestivalRegistrationResponse]


class RegistrationFormLinkPage(PageBase):
    items: list[RegistrationFormLinkResponse]


# Forward references
from .user import UserResponse  # noqa: E402
from .role import RoleResponse  # noqa: E402
from .festival import FestivalResponse  # noqa: E402
from .participant_tag import ParticipantTagResponse  # noqa: E402

RegistrationFormResponse.model_rebuild()
RegistrationFormPublicResponse.model_rebuild()
RegistrationFormSectionResponse.model_rebuild()
RegistrationFormSectionRoleResponse.model_rebuild()
RegistrationFormSectionTagResponse.model_rebuild()
FestivalRegistrationResponse.model_rebuild()
RegistrationSectionSelectionResponse.model_rebuild()
