"""Router for validation rules and validation rule groups."""

from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.validation_rule import (
    ValidationRuleCreate,
    ValidationRuleUpdate,
    ValidationRuleResponse,
    ValidationRulesPage,
    ValidationRuleGroupCreate,
    ValidationRuleGroupResponse,
    ValidationRuleGroupsPage,
)
from app.services.validation_rule_service import ValidationRuleService, ValidationRuleGroupService
from app.routers.permissions import is_admin
from app.models.user import User

router = APIRouter()

validation_rule_service = ValidationRuleService()
validation_rule_group_service = ValidationRuleGroupService()


def require_admin(user: User):
    if not is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


@router.get("/validation-rules/", response_model=ValidationRulesPage)
async def list_validation_rules(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    scope: str | None = None,
    scope_id: int | None = None,
    db: Session = Depends(get_db),
):
    return validation_rule_service.get_all_paginated(db, page, size, scope, scope_id)


@router.post("/validation-rules/", response_model=ValidationRuleResponse, status_code=201)
async def create_validation_rule(
    rule: ValidationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return validation_rule_service.create(db, rule)


@router.get("/validation-rules/{rule_id}", response_model=ValidationRuleResponse)
async def get_validation_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = validation_rule_service.get(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Validation rule not found")
    return rule


@router.put("/validation-rules/{rule_id}", response_model=ValidationRuleResponse)
async def update_validation_rule(
    rule_id: int,
    rule: ValidationRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    updated = validation_rule_service.update(db, rule_id, rule)
    if not updated:
        raise HTTPException(status_code=404, detail="Validation rule not found")
    return updated


@router.delete("/validation-rules/{rule_id}")
async def delete_validation_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    deleted = validation_rule_service.delete(db, rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Validation rule not found")
    return {"message": "Validation rule deleted"}


@router.get("/validation-rule-groups/", response_model=ValidationRuleGroupsPage)
async def list_validation_rule_groups(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    scope: str | None = None,
    db: Session = Depends(get_db),
):
    return validation_rule_group_service.get_all_paginated(db, page, size, scope)


@router.post("/validation-rule-groups/", response_model=ValidationRuleGroupResponse, status_code=201)
async def create_validation_rule_group(
    group: ValidationRuleGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return validation_rule_group_service.create_with_rules(db, group)
