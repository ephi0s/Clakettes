"""Jury voting endpoints (Fase 5)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.jury_vote_service import JuryVoteService

router = APIRouter(prefix="/jury-votes", tags=["jury-votes"])
service = JuryVoteService()


class VoteIn(BaseModel):
    festival_id: int
    shortfilm_id: int
    score: float
    comment: str | None = None


@router.post("")
async def cast_vote(body: VoteIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = service.cast(db, body.festival_id, current_user.id, body.shortfilm_id, body.score, body.comment)
    return {"id": v.id, "score": v.score}


@router.get("/{festival_id}")
async def list_votes(festival_id: int, db: Session = Depends(get_db)):
    return [
        {"id": v.id, "juror_id": v.juror_id, "shortfilm_id": v.shortfilm_id, "score": v.score}
        for v in service.list_for_festival(db, festival_id)
    ]


@router.get("/aggregate/{festival_id}")
async def aggregate_votes(festival_id: int, db: Session = Depends(get_db)):
    votes = service.list_for_festival(db, festival_id)
    agg = {}
    for v in votes:
        agg.setdefault(v.shortfilm_id, []).append(v.score)
    return {sid: (sum(s) / len(s)) for sid, s in agg.items()}


@router.get("/by-juror/{festival_id}/{juror_id}")
async def votes_by_juror(festival_id: int, juror_id: int, db: Session = Depends(get_db)):
    votes = [v for v in service.list_for_festival(db, festival_id) if v.juror_id == juror_id]
    return [{"shortfilm_id": v.shortfilm_id, "score": v.score} for v in votes]


@router.get("/anonymous/{festival_id}")
async def anonymous_votes(festival_id: int, db: Session = Depends(get_db)):
    votes = service.list_for_festival(db, festival_id)
    return [{"shortfilm_id": v.shortfilm_id, "score": v.score} for v in votes]
