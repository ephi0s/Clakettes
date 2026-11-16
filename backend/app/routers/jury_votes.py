"""Jury voting endpoints (Fase 5)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.routers.dependencies import get_current_user_optional
from app.models.user import User
from app.services.jury_vote_service import JuryVoteService
from app.schemas.jury_vote import VoteIn, VoteOut, VoteAggregate, FestivalAggregate

router = APIRouter(prefix="/jury-votes", tags=["jury-votes"])
service = JuryVoteService()


@router.post("", response_model=VoteOut, status_code=status.HTTP_201_CREATED)
async def cast_vote(
    body: VoteIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        v = service.cast(
            db,
            body.festival_id,
            current_user.id,
            body.shortfilm_id,
            body.score,
            body.comment,
            body.anonymous,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return VoteOut(
        id=v.id,
        festival_id=v.festival_id,
        juror_id=v.juror_id,
        shortfilm_id=v.shortfilm_id,
        score=v.score,
        comment=v.comment,
        anonymous=v.anonymous,
        created_at=v.created_at,
    )


@router.get("/{festival_id}", response_model=list[VoteOut])
async def list_votes(
    festival_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    from app.routers.permissions import is_admin

    votes = service.list_for_festival(db, festival_id, include_anonymous=False)
    items = []
    for v in votes:
        items.append(
            VoteOut(
                id=v.id,
                festival_id=v.festival_id,
                juror_id=v.juror_id,
                shortfilm_id=v.shortfilm_id,
                score=v.score,
                comment=v.comment,
                anonymous=v.anonymous,
                created_at=v.created_at,
            )
        )
    # Los votos anónimos se filtran en el servicio salvo admin.
    if current_user is not None and is_admin(current_user):
        all_votes = service.list_for_festival(db, festival_id, include_anonymous=True)
        seen = {v.id for v in votes}
        for v in all_votes:
            if v.id not in seen:
                items.append(
                    VoteOut(
                        id=v.id,
                        festival_id=v.festival_id,
                        juror_id=None,
                        shortfilm_id=v.shortfilm_id,
                        score=v.score,
                        comment=v.comment,
                        anonymous=True,
                        created_at=v.created_at,
                    )
                )
    return items


@router.get("/aggregate/{festival_id}", response_model=FestivalAggregate)
async def aggregate_votes(festival_id: int, db: Session = Depends(get_db)):
    results = service.aggregate(db, festival_id)
    return FestivalAggregate(
        festival_id=festival_id,
        results=[
            VoteAggregate(
                shortfilm_id=r["shortfilm_id"],
                average_score=r["average_score"],
                vote_count=r["vote_count"],
                scores=r["scores"],
            )
            for r in results
        ],
    )


@router.get("/by-juror/{festival_id}/{juror_id}")
async def votes_by_juror(
    festival_id: int,
    juror_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.routers.permissions import is_admin

    votes = service.list_for_festival(db, festival_id, include_anonymous=False)
    items = []
    for v in votes:
        if v.juror_id == juror_id:
            items.append(
                {
                    "shortfilm_id": v.shortfilm_id,
                    "score": v.score,
                }
            )
    # Solo admin puede ver votos ajenos
    if current_user is None or (current_user.id != juror_id and not is_admin(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return items


@router.get("/anonymous/{festival_id}")
async def anonymous_votes(
    festival_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.routers.permissions import is_admin

    if current_user is None or not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    votes = service.list_for_festival(db, festival_id, include_anonymous=True)
    return [
        {
            "shortfilm_id": v.shortfilm_id,
            "score": v.score,
            "comment": v.comment,
        }
        for v in votes
        if v.anonymous
    ]
