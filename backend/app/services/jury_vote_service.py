"""Service for jury voting (Fase 5)."""

from sqlalchemy.orm import Session
from app.models.jury_vote import JuryVote


class JuryVoteService:
    def cast(
        self, db: Session, festival_id: int, juror_id: int, shortfilm_id: int, score: float, comment: str | None = None
    ) -> JuryVote:
        obj = JuryVote(
            festival_id=festival_id, juror_id=juror_id, shortfilm_id=shortfilm_id, score=score, comment=comment
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_for_festival(self, db: Session, festival_id: int):
        return db.query(JuryVote).filter(JuryVote.festival_id == festival_id).all()
