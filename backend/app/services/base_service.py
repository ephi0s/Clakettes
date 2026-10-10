"""Generic CRUD base service with type-safe operations.

All entity services inherit from this base to get consistent CRUD + pagination.
Uses SQLAlchemy 2.0 style with Pydantic v2 model_dump().
"""

from sqlalchemy.orm import Query, Session
from typing import Generic, TypeVar, Type, Optional
from pydantic import BaseModel
from pydantic.networks import AnyUrl

# Type variables for generic CRUD
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD service parameterised by the model and its schemas.

    Provides ``get``, ``create``, ``update`` (partial), ``delete``,
    and ``paginate`` for building paginated responses.

    Usage:
        class UserService(BaseService[User, UserCreate, UserUpdate]):
            pass

        user_service = UserService(User)
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Fetch single record by primary key."""
        return db.query(self.model).filter(self.model.id == id).first()

    @staticmethod
    def _dump(obj_in: BaseModel, exclude_unset: bool = False) -> dict:
        data = obj_in.model_dump(exclude_unset=exclude_unset)
        for key, value in data.items():
            if isinstance(value, AnyUrl):
                data[key] = str(value)
        return data

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create new record from Pydantic schema.

        Uses model_dump() to convert schema to dict, then instantiates model.
        Commits and refreshes to get DB-generated fields (id, timestamps).
        """
        obj_data = self._dump(obj_in)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Partial update — only fields provided in schema are modified.

        Uses exclude_unset=True to ignore fields not sent in request.
        Returns None if record not found.
        """
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        update_data = self._dump(obj_in, exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        """Delete record by ID. Returns deleted object or None if not found."""
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        db.delete(db_obj)
        db.commit()
        return db_obj

    MAX_PAGE_SIZE = 100

    def paginate(self, query: Query, page: int, size: int) -> dict:
        """Apply pagination to a query and return standard envelope.

        Args:
            query: SQLAlchemy query (already filtered/ordered)
            page: 1-based page number (clamped to >= 1)
            size: Page size, clamped to [1, MAX_PAGE_SIZE] to bound memory/latency

        Returns:
            Dict with items, total, page, size, pages — matches API response format
        """
        page = max(1, page)
        size = min(max(1, size), self.MAX_PAGE_SIZE)
        total = query.order_by(None).count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": max(1, (total + size - 1) // size),
        }

    def paginate_filtered(self, db: Session, page: int, size: int, *filters, order_by=None) -> dict:
        """Paginate ``self.model`` with SQL-side filters (avoids in-memory pagination).

        Replaces the per-service ``get_all_paginated`` clones: filters run in SQL
        so only the requested page is fetched. Use for simple equality filters;
        build a custom query + paginate() for joins/eager loading.
        """
        query = db.query(self.model)
        for criterion in filters:
            query = query.filter(criterion)
        if order_by is not None:
            query = query.order_by(order_by)
        return self.paginate(query, page, size)
