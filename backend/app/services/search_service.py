from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.festival import Festival
from app.models.user import User
from app.models.shortfilm import ShortFilm


class SearchService:
    def search_all(self, db: Session, q: str, type: str = "all") -> dict:
        results: dict = {"festivals": [], "users": [], "shortfilms": []}

        if type in ("all", "festivals"):
            festivals = (
                db.query(Festival)
                .filter(
                    or_(
                        Festival.name.ilike(f"%{q}%"),
                        Festival.description.ilike(f"%{q}%"),
                        Festival.location.ilike(f"%{q}%"),
                    )
                )
                .limit(20)
                .all()
            )
            results["festivals"] = [
                {"id": f.id, "name": f.name, "location": f.location, "is_active": f.is_active} for f in festivals
            ]

        if type in ("all", "users"):
            users = (
                db.query(User)
                .filter(or_(User.username.ilike(f"%{q}%"), User.full_name.ilike(f"%{q}%")))
                .filter(User.is_public)
                .limit(20)
                .all()
            )
            results["users"] = [{"id": u.id, "username": u.username, "full_name": u.full_name} for u in users]

        if type in ("all", "shortfilms"):
            films = (
                db.query(ShortFilm)
                .filter(
                    or_(
                        ShortFilm.title.ilike(f"%{q}%"),
                        ShortFilm.description.ilike(f"%{q}%"),
                        ShortFilm.tags.ilike(f"%{q}%"),
                    )
                )
                .filter(ShortFilm.is_public)
                .limit(20)
                .all()
            )
            results["shortfilms"] = [
                {"id": f.id, "title": f.title, "duration": f.duration, "user_id": f.user_id} for f in films
            ]

        return results
