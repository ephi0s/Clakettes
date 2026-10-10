from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.festival import Festival
from app.models.user_festival import user_festival


class UserFestivalService:
    def join_festival(self, db: Session, user_id: int, festival_id: int, role: str | None = None) -> None:
        db.execute(user_festival.insert().values(user_id=user_id, festival_id=festival_id, role=role))
        db.commit()

    def leave_festival(self, db: Session, user_id: int, festival_id: int) -> bool:
        result = db.execute(
            user_festival.delete().where(
                user_festival.c.user_id == user_id,
                user_festival.c.festival_id == festival_id,
            )
        )
        db.commit()
        return result.rowcount > 0

    def is_member(self, db: Session, user_id: int, festival_id: int) -> bool:
        existing = db.execute(
            select(user_festival).where(
                user_festival.c.user_id == user_id,
                user_festival.c.festival_id == festival_id,
            )
        ).first()
        return existing is not None

    def get_festival_members(self, db: Session, festival_id: int) -> list[dict]:
        rows = (
            db.query(User, user_festival.c.role, user_festival.c.joined_at)
            .join(user_festival, User.id == user_festival.c.user_id)
            .filter(user_festival.c.festival_id == festival_id)
            .all()
        )
        members = []
        for row in rows:
            user = row.User
            members.append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": row.role,
                    "joined_at": str(row.joined_at) if row.joined_at else None,
                }
            )
        return members

    def get_user_festivals(self, db: Session, user_id: int) -> list[dict]:
        rows = (
            db.query(Festival, user_festival.c.role, user_festival.c.joined_at)
            .join(user_festival, Festival.id == user_festival.c.festival_id)
            .filter(user_festival.c.user_id == user_id)
            .all()
        )
        festivals = []
        for row in rows:
            festival = row.Festival
            festivals.append(
                {
                    "festival_id": festival.id,
                    "name": festival.name,
                    "location": festival.location,
                    "role": row.role,
                    "joined_at": str(row.joined_at) if row.joined_at else None,
                }
            )
        return festivals
