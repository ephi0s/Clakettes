"""Router for user alias management."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.user_alias import (
    UserAliasCreate,
    UserAliasUpdate,
    UserAliasResponse,
    UserAliasesPage,
)
from app.services.user_alias_service import UserAliasService
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()

user_service = UserService()
user_alias_service = UserAliasService()


@router.get("/users/{user_id}/aliases/", response_model=UserAliasesPage)
async def list_user_aliases(
    user_id: int,
    page: int = 1,
    size: int = 20,
    context: str | None = None,
    db: Session = Depends(get_db),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_alias_service.get_by_user_paginated(db, user_id, page, size, context)


@router.post("/users/{user_id}/aliases/", response_model=UserAliasResponse, status_code=201)
async def create_user_alias(
    user_id: int,
    alias: UserAliasCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = alias.model_dump()
    data["user_id"] = user_id
    if not data.get("profile_token"):
        data["profile_token"] = uuid.uuid4().hex
    create_data = UserAliasCreate(**data)
    return user_alias_service.create(db, create_data)


@router.put("/users/{user_id}/aliases/{alias_id}", response_model=UserAliasResponse)
async def update_user_alias(
    user_id: int,
    alias_id: int,
    alias: UserAliasUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = user_alias_service.get(db, alias_id)
    if not existing or existing.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alias not found")
    updated = user_alias_service.update(db, alias_id, alias)
    return updated


@router.delete("/users/{user_id}/aliases/{alias_id}")
async def delete_user_alias(
    user_id: int,
    alias_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = user_alias_service.get(db, alias_id)
    if not existing or existing.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alias not found")
    user_alias_service.delete(db, alias_id)
    return {"message": "Alias deleted"}
