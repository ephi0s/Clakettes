"""Notification service — CRUD and unread count for in-app notifications."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from .base_service import BaseService


class NotificationService(BaseService[Notification, NotificationCreate, None]):
    def __init__(self):
        super().__init__(Notification)

    def get_multi_paginated(
        self, db: Session, page: int = 1, size: int = 20, user_id: int | None = None, is_read: bool | None = None
    ):
        filters = []
        if user_id is not None:
            filters.append(Notification.user_id == user_id)
        if is_read is not None:
            filters.append(Notification.is_read == is_read)
        return self.paginate_filtered(db, page, size, *filters, order_by=Notification.created_at.desc())

    def get_unread_count(self, db: Session, user_id: int) -> int:
        return (
            db.query(func.count(Notification.id))
            .filter(
                Notification.user_id == user_id,
                ~Notification.is_read,
            )
            .scalar()
        )

    def mark_as_read(self, db: Session, notification_id: int, user_id: int) -> Notification | None:
        notif = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )
        if not notif:
            return None
        notif.is_read = True
        db.commit()
        db.refresh(notif)
        return notif

    def mark_all_as_read(self, db: Session, user_id: int) -> int:
        count = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                ~Notification.is_read,
            )
            .update({"is_read": True})
        )
        db.commit()
        return count

    def create_notification(
        self,
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "profile_update",
        related_user_id: int | None = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_user_id=related_user_id,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif
