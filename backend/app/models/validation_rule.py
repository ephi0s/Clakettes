"""ValidationRule model — defines required fields and validation per role/festival."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON, Enum as SQLEnum, Table
from app.models.base import BaseModel, Base
from app.enums import ValidationScope, FieldType


class ValidationRule(BaseModel):
    """Defines required/optional fields and validation for user profiles in a given scope."""

    __tablename__ = "validation_rules"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    scope = Column(
        SQLEnum(ValidationScope, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ValidationScope.GLOBAL,
    )
    scope_id = Column(Integer, nullable=True, index=True)
    field_name = Column(String(100), nullable=False)
    field_label = Column(String(200), nullable=False)
    field_type = Column(
        SQLEnum(FieldType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=FieldType.STRING
    )
    is_required = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    is_editable_by_user = Column(Boolean, default=True)
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)
    regex_pattern = Column(String(500), nullable=True)
    allowed_values = Column(JSON, nullable=True)
    default_value = Column(Text, nullable=True)
    help_text = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    depends_on_field = Column(String(100), nullable=True)
    depends_on_value = Column(String(500), nullable=True)
    error_message = Column(String(500), nullable=True)

    def __repr__(self):
        scope_str = f"{self.scope.value}"
        if self.scope_id:
            scope_str += f":{self.scope_id}"
        return f"<ValidationRule(field='{self.field_name}', scope={scope_str}, required={self.is_required})>"


class ValidationRuleGroup(BaseModel):
    """Groups validation rules for easier management."""

    __tablename__ = "validation_rule_groups"

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    scope = Column(SQLEnum(ValidationScope, values_callable=lambda x: [e.value for e in x]), nullable=False)
    scope_id = Column(Integer, nullable=True, index=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ValidationRuleGroup(name='{self.name}', scope={self.scope.value})>"


validation_rule_group_rules = Table(
    "validation_rule_group_rules",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("validation_rule_groups.id"), primary_key=True),
    Column("rule_id", Integer, ForeignKey("validation_rules.id"), primary_key=True),
)
