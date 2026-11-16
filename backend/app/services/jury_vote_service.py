"""Service for jury voting (Fase 5).

Valida que el votante tenga rol de jurado, impide votos duplicados
(un jurado vota una vez por cortometraje) y soporta votos anónimos.
"""

from sqlalchemy.orm import Session

from app.models.jury_vote import JuryVote
from app.models.festival import Festival
from app.models.shortfilm import ShortFilm
from app.models.user import User
from app.models.user_role import UserRole, UserRoleStatus
from app.models.role import Role
from app.models.event import Event
from app.models.event_screening import EventScreening


class JuryVoteService:
    def _is_jury_or_above(self, db: Session, user_id: int, festival_id: int) -> bool:
        """Devuelve True si el usuario puede votar en el festival.

        Puede votar quien tenga rol jury (global o en el festival),
        organizer del festival, o admin global.
        """
        from app.routers.permissions import _is_admin, _is_organizer_of_festival

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return False
        if _is_admin(db, user):
            return True
        if _is_organizer_of_festival(db, user_id, festival_id):
            return True
        # Rol de jurado: activo/aprobado, global o festival-scoped
        jury = (
            db.query(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user_id,
                Role.name == "jury",
                UserRole.status.in_([UserRoleStatus.ACTIVE, UserRoleStatus.APPROVED]),
                (UserRole.festival_id == festival_id) | (UserRole.festival_id.is_(None)),
            )
            .first()
        )
        return jury is not None

    def _already_voted(self, db: Session, festival_id: int, juror_id: int, shortfilm_id: int) -> bool:
        return (
            db.query(JuryVote)
            .filter(
                JuryVote.festival_id == festival_id,
                JuryVote.juror_id == juror_id,
                JuryVote.shortfilm_id == shortfilm_id,
            )
            .first()
            is not None
        )

    def _is_eligible_for_voting(self, db: Session, festival_id: int, shortfilm_id: int) -> tuple[bool, str | None]:
        """Devuelve (elegible, motivo) verificando el estado de cribado de la obra.

        Una obra no es elegible para voto si en algún evento de cribado del
        festival tiene estado 'disqualified'.
        """
        rows = (
            db.query(EventScreening)
            .join(Event, Event.id == EventScreening.event_id)
            .filter(
                Event.festival_id == festival_id,
                EventScreening.shortfilm_id == shortfilm_id,
                EventScreening.status == "disqualified",
            )
            .all()
        )
        if rows:
            reason = rows[0].status_reason or "Obra descalificada en el cribado"
            return False, reason
        return True, None

    def cast(
        self,
        db: Session,
        festival_id: int,
        juror_id: int,
        shortfilm_id: int,
        score: float,
        comment: str | None = None,
        anonymous: bool = False,
    ) -> JuryVote:
        """Registra un voto de jurado.

        Reglas:
        - El juror debe tener rol de jurado (o organizer/admin del festival).
        - No puede votar dos veces el mismo cortometraje en el mismo festival.
        - El score debe estar en [0, 10].
        - La obra no debe estar descalificada en el cribado del festival.
        """
        if not (0 <= score <= 10):
            raise ValueError("Score must be between 0 and 10")
        if not self._is_jury_or_above(db, juror_id, festival_id):
            raise PermissionError("User is not a jury member for this festival")
        if self._already_voted(db, festival_id, juror_id, shortfilm_id):
            raise ValueError("Juror already voted for this shortfilm in this festival")
        # Verificar que el festival y el shortfilm existan
        festival = db.query(Festival).filter(Festival.id == festival_id).first()
        if festival is None:
            raise ValueError("Festival not found")
        shortfilm = db.query(ShortFilm).filter(ShortFilm.id == shortfilm_id).first()
        if shortfilm is None:
            raise ValueError("ShortFilm not found")
        # Elegibilidad por cribado: no votar obras descalificadas.
        eligible, reason = self._is_eligible_for_voting(db, festival_id, shortfilm_id)
        if not eligible:
            raise PermissionError(reason or "La obra no es elegible para votación")

        juror_id_to_store = None if anonymous else juror_id
        obj = JuryVote(
            festival_id=festival_id,
            juror_id=juror_id_to_store,
            shortfilm_id=shortfilm_id,
            score=score,
            comment=comment,
            anonymous=anonymous,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_for_festival(self, db: Session, festival_id: int, include_anonymous: bool = False):
        query = db.query(JuryVote).filter(JuryVote.festival_id == festival_id)
        if not include_anonymous:
            query = query.filter(JuryVote.anonymous.is_(False))
        return query.all()

    def aggregate(self, db: Session, festival_id: int) -> list[dict]:
        """Devuelve agregación por cortometraje: promedio, conteo y scores."""
        votes = self.list_for_festival(db, festival_id, include_anonymous=True)
        agg: dict[int, list[float]] = {}
        for v in votes:
            agg.setdefault(v.shortfilm_id, []).append(v.score)
        results = []
        for shortfilm_id, scores in sorted(agg.items()):
            results.append(
                {
                    "shortfilm_id": shortfilm_id,
                    "average_score": round(sum(scores) / len(scores), 2),
                    "vote_count": len(scores),
                    "scores": scores,
                }
            )
        return results
