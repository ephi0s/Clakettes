"""Services for ValidationRule and ValidationRuleGroup."""

from sqlalchemy.orm import Session
from app.models.validation_rule import ValidationRule, ValidationRuleGroup, validation_rule_group_rules
from app.schemas.validation_rule import (
    ValidationRuleCreate,
    ValidationRuleUpdate,
    ValidationRuleGroupCreate,
    ValidationRuleGroupUpdate,
)
from .base_service import BaseService


class ValidationRuleService(BaseService[ValidationRule, ValidationRuleCreate, ValidationRuleUpdate]):
    def __init__(self):
        super().__init__(ValidationRule)

    def get_all(self, db: Session, scope: str | None = None, scope_id: int | None = None) -> list:
        query = db.query(ValidationRule)
        if scope:
            query = query.filter(ValidationRule.scope == scope)
        if scope_id is not None:
            query = query.filter(ValidationRule.scope_id == scope_id)
        return query.order_by(ValidationRule.display_order).all()

    def get_all_paginated(
        self,
        db: Session,
        page: int,
        size: int,
        scope: str | None = None,
        scope_id: int | None = None,
    ) -> dict:
        query = db.query(ValidationRule)
        if scope:
            query = query.filter(ValidationRule.scope == scope)
        if scope_id is not None:
            query = query.filter(ValidationRule.scope_id == scope_id)
        return self.paginate(query.order_by(ValidationRule.display_order), page, size)


class ValidationRuleGroupService(
    BaseService[ValidationRuleGroup, ValidationRuleGroupCreate, ValidationRuleGroupUpdate]
):
    def __init__(self):
        super().__init__(ValidationRuleGroup)

    def get_all(self, db: Session, scope: str | None = None) -> list:
        query = db.query(ValidationRuleGroup)
        if scope:
            query = query.filter(ValidationRuleGroup.scope == scope)
        return query.all()

    def get_all_paginated(self, db: Session, page: int, size: int, scope: str | None = None) -> dict:
        query = db.query(ValidationRuleGroup)
        if scope:
            query = query.filter(ValidationRuleGroup.scope == scope)
        return self.paginate(query, page, size)

    def create_with_rules(self, db: Session, obj_in: ValidationRuleGroupCreate):
        group_data = obj_in.model_dump(exclude={"rule_ids"})
        db_obj = ValidationRuleGroup(**group_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        if obj_in.rule_ids:
            for rid in obj_in.rule_ids:
                db.execute(validation_rule_group_rules.insert().values(group_id=db_obj.id, rule_id=rid))
            db.commit()
        return db_obj
