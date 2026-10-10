from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate
from .base_service import BaseService


class MessageService(BaseService[Message, MessageCreate, MessageUpdate]):
    def __init__(self):
        super().__init__(Message)

    def get_multi_paginated(
        self,
        db: Session,
        page: int = 1,
        size: int = 50,
        sender_id: int | None = None,
        receiver_id: int | None = None,
        group_id: int | None = None,
        channel_id: int | None = None,
        unread_only: bool = False,
        user_id: int | None = None,
    ):
        query = db.query(Message)
        if user_id is not None and group_id is None and channel_id is None:
            # DM scope: restrict to conversations where the caller is a participant
            query = query.filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
        if sender_id:
            query = query.filter(Message.sender_id == sender_id)
        if receiver_id:
            query = query.filter(Message.receiver_id == receiver_id)
        if group_id:
            query = query.filter(Message.group_id == group_id)
        if channel_id:
            query = query.filter(Message.channel_id == channel_id)
        if unread_only:
            query = query.filter(~Message.is_read)
        query = query.order_by(Message.created_at.desc())
        return self.paginate(query, page, size)

    def mark_as_read(self, db: Session, message_id: int) -> Message | None:
        message = self.get(db, message_id)
        if message:
            message.is_read = True
            db.commit()
            db.refresh(message)
        return message
