from pydantic import BaseModel, ConfigDict
from typing import Any
from datetime import datetime
from .common import PageBase
from app.enums import ValidationScope, FieldType


class ValidationRuleBase(BaseModel):
    name: str
    description: str | None = None
    scope: str = ValidationScope.GLOBAL.value
    scope_id: int | None = None
    field_name: str
    field_label: str
    field_type: str = FieldType.STRING.value
    is_required: bool = False
    is_visible: bool = True
    is_editable_by_user: bool = True
    min_length: int | None = None
    max_length: int | None = None
    regex_pattern: str | None = None
    allowed_values: list[Any] | None = None
    default_value: str | None = None
    help_text: str | None = None
    display_order: int = 0
    depends_on_field: str | None = None
    depends_on_value: str | None = None
    error_message: str | None = None


class ValidationRuleCreate(ValidationRuleBase):
    pass


class ValidationRuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    scope: str | None = None
    scope_id: int | None = None
    field_name: str | None = None
    field_label: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    is_visible: bool | None = None
    is_editable_by_user: bool | None = None
    min_length: int | None = None
    max_length: int | None = None
    regex_pattern: str | None = None
    allowed_values: list[Any] | None = None
    default_value: str | None = None
    help_text: str | None = None
    display_order: int | None = None
    depends_on_field: str | None = None
    depends_on_value: str | None = None
    error_message: str | None = None
    is_active: bool | None = None


class ValidationRuleResponse(ValidationRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ValidationRuleGroupBase(BaseModel):
    name: str
    description: str | None = None
    scope: str = ValidationScope.GLOBAL.value
    scope_id: int | None = None
    is_active: bool = True


class ValidationRuleGroupCreate(ValidationRuleGroupBase):
    rule_ids: list[int] = []


class ValidationRuleGroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    scope: str | None = None
    scope_id: int | None = None
    is_active: bool | None = None
    rule_ids: list[int] | None = None


class ValidationRuleGroupResponse(ValidationRuleGroupBase):
    id: int
    created_at: datetime
    updated_at: datetime
    rules: list[ValidationRuleResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ValidationRulesPage(PageBase):
    items: list[ValidationRuleResponse]


class ValidationRuleGroupsPage(PageBase):
    items: list[ValidationRuleGroupResponse]
