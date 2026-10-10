import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base_service import BaseService


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_multi_paginated(
        self, db: Session, page: int = 1, size: int = 20, is_active: bool | None = None, role: str | None = None
    ):
        query = db.query(User)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if role:
            query = query.filter(User.role == role)
        return self.paginate(query, page, size)

    def get_public_users(self, db: Session, page: int = 1, size: int = 50) -> list[dict]:
        """Return users with only their publicly visible fields."""
        query = db.query(User).filter(User.is_public)
        users = query.offset((page - 1) * size).limit(size).all()
        return [self.to_public_response(u) for u in users]

    def to_public_response(self, user: User) -> dict:
        """Build a public-safe dict from a User model, respecting per-field privacy."""
        data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name if user.is_public else None,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        if user.is_public_email:
            data["email"] = user.email
        if user.is_public_bio:
            data["bio"] = user.bio
        if user.is_public_location:
            data["latitude"] = user.latitude
            data["longitude"] = user.longitude
        return data

    def to_authenticated_public_response(self, user: User) -> dict:
        """Public-safe dict for authenticated non-admin viewers — email never included."""
        data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name if user.is_public else None,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        if user.is_public_bio:
            data["bio"] = user.bio
        if user.is_public_location:
            data["latitude"] = user.latitude
            data["longitude"] = user.longitude
        return data

    def create(self, db: Session, obj_in: UserCreate) -> User:
        obj_data = obj_in.model_dump()
        obj_data["password_hash"] = hash_password(obj_data.pop("password"))
        db_obj = User(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, username: str, password: str) -> User | None:
        user = self.get_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> User | None:
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        password = update_data.pop("password", None)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        if password:
            db_obj.password_hash = hash_password(password)
        db.commit()
        db.refresh(db_obj)
        return db_obj
