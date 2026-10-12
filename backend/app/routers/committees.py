"""Router for committees and committee members."""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.committee import (
    CommitteeCreate,
    CommitteeUpdate,
    CommitteeResponse,
    CommitteePage,
    CommitteeMemberCreate,
    CommitteeMemberUpdate,
    CommitteeMemberResponse,
    CommitteeMemberPage,
)
from app.services.group_service import CommitteeService, CommitteeMemberService
from app.models.committee import Committee, CommitteeMember
from app.models.festival import Festival
from app.routers.permissions import require_festival_admin
from app.routers.dependencies import get_current_user_optional, get_or_404
from app.models.user import User

router = APIRouter()

committee_service = CommitteeService()
committee_member_service = CommitteeMemberService()


@router.get("/festivals/{festival_id}/committees/", response_model=CommitteePage)
async def list_committees(
    festival_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    get_or_404(db, Festival, festival_id, "Festival")
    result = committee_service.get_by_festival_paginated(db, festival_id, page, size)
    counts = committee_service.get_member_counts(db, [c.id for c in result["items"]])
    for c in result["items"]:
        c.member_count = counts.get(c.id, 0)
    return result


@router.post("/festivals/{festival_id}/committees/", response_model=CommitteeResponse, status_code=201)
async def create_committee(
    festival_id: int,
    obj: CommitteeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, Festival, festival_id, "Festival")
    require_festival_admin(db, current_user, festival_id)
    data = obj.model_dump()
    data["festival_id"] = festival_id
    create_data = CommitteeCreate(**data)
    return committee_service.create(db, create_data)


@router.get("/committees/{committee_id}", response_model=CommitteeResponse)
async def get_committee(
    committee_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
):
    committee = get_or_404(db, Committee, committee_id, "Committee")
    committee.member_count = committee_service.get_member_count(db, committee.id)
    return committee


@router.put("/committees/{committee_id}", response_model=CommitteeResponse)
async def update_committee(
    committee_id: int,
    obj: CommitteeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    committee = get_or_404(db, Committee, committee_id, "Committee")
    require_festival_admin(db, current_user, committee.festival_id)
    updated = committee_service.update(db, committee_id, obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Committee not found")
    return updated


@router.delete("/committees/{committee_id}")
async def delete_committee(
    committee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    committee = get_or_404(db, Committee, committee_id, "Committee")
    require_festival_admin(db, current_user, committee.festival_id)
    deleted = committee_service.delete(db, committee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Committee not found")
    return {"message": "Committee deleted"}


@router.get("/committees/{committee_id}/members/", response_model=CommitteeMemberPage)
async def list_committee_members(
    committee_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    get_or_404(db, Committee, committee_id, "Committee")
    return committee_member_service.get_by_committee_paginated(db, committee_id, page, size)


@router.post("/committees/{committee_id}/members/", response_model=CommitteeMemberResponse, status_code=201)
async def add_committee_member(
    committee_id: int,
    obj: CommitteeMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    committee = get_or_404(db, Committee, committee_id, "Committee")
    require_festival_admin(db, current_user, committee.festival_id)
    data = obj.model_dump()
    data["committee_id"] = committee_id
    existing = committee_member_service.get_membership(db, committee_id, data["user_id"])
    if existing:
        raise HTTPException(status_code=400, detail="User already a member of this committee")
    create_data = CommitteeMemberCreate(**data)
    return committee_member_service.create(db, create_data)


@router.put("/committee-members/{member_id}", response_model=CommitteeMemberResponse)
async def update_committee_member(
    member_id: int,
    obj: CommitteeMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = get_or_404(db, CommitteeMember, member_id, "Member")
    committee = get_or_404(db, Committee, member.committee_id, "Committee")
    require_festival_admin(db, current_user, committee.festival_id)
    updated = committee_member_service.update(db, member_id, obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated


@router.delete("/committee-members/{member_id}")
async def remove_committee_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = get_or_404(db, CommitteeMember, member_id, "Member")
    committee = get_or_404(db, Committee, member.committee_id, "Committee")
    require_festival_admin(db, current_user, committee.festival_id)
    deleted = committee_member_service.delete(db, member_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member removed"}
