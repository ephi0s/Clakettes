"""Message model — P2P and group chat messages with rich content support."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Message(BaseModel):
    """A chat message between users, supporting both P2P and group conversations.

    Message types (``message_type``):
        - ``text``: plain text content
        - ``image``: image sent via media_url
        - ``location``: geographic coordinates (latitude / longitude)
        - ``vcard``: contact card data (JSON in vcard_data)
        - ``ical``: calendar event data (JSON in ical_data)

    Relationships:
        sender: The user who sent the message.
        receiver: The P2P recipient (None for group messages).
    """

    __tablename__ = "messages"

    content = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    group_id = Column(Integer, nullable=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True, index=True)
    is_read = Column(Boolean, default=False)

    # Rich content fields
    message_type = Column(String(20), nullable=False, default="text")
    media_url = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    vcard_data = Column(Text, nullable=True)
    ical_data = Column(Text, nullable=True)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    channel = relationship("Channel", foreign_keys=[channel_id])
