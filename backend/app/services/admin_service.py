from sqlalchemy.orm import Session
from sqlalchemy import inspect as sa_inspect, func, select
from app.models.base import Base
from app.models.user import User
from app.models.festival import Festival
from app.models.shortfilm import ShortFilm
from app.models.message import Message


class AdminService:
    def get_stats(self, db: Session) -> dict:
        return {
            "users": db.query(func.count(User.id)).scalar(),
            "festivals": db.query(func.count(Festival.id)).scalar(),
            "shortfilms": db.query(func.count(ShortFilm.id)).scalar(),
            "messages": db.query(func.count(Message.id)).scalar(),
            "active_users": db.query(func.count(User.id)).filter(User.is_active).scalar(),
            "active_festivals": db.query(func.count(Festival.id)).filter(Festival.is_active).scalar(),
        }

    def get_tables(self, db: Session) -> dict:
        inspector = sa_inspect(db.get_bind())
        tables = {}
        for table_name in inspector.get_table_names():
            if table_name == "alembic_version":
                continue
            model = Base.metadata.tables.get(table_name)
            if model is not None:
                count = db.execute(select(func.count()).select_from(model)).scalar()
                tables[table_name] = count
        return {"tables": tables}

    def reset_database(self, db: Session) -> dict:
        bind = db.get_bind()
        db.close()
        Base.metadata.drop_all(bind=bind)
        Base.metadata.create_all(bind=bind)
        return {"message": "Database reset complete"}
