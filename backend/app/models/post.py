"""Post model — microblogging wall publications for user and festival profiles."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Post(BaseModel):
    """A wall publication (microblogging post) on a user or festival profile.

    Top-level posts target exactly one wall (``target_user_id`` xor
    ``festival_id``). Replies reference ``parent_post_id`` and inherit the
    parent scope. ``embed_url``/``embed_type`` hold recognized multimedia
    embeds (youtube, vimeo, dailymotion, odysee, ivoox, podimo, generic).
    Image/animation attachments are reserved for future use and stay disabled.
    """

    __tablename__ = "posts"

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    parent_post_id = Column(Integer, ForeignKey("posts.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    embed_url = Column(String(1000), nullable=True)
    embed_type = Column(String(30), nullable=True)
    allow_replies = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)

    author = relationship("User", foreign_keys=[author_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    festival = relationship("Festival")
    replies = relationship("Post", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("Post", back_populates="replies", remote_side="Post.id")
