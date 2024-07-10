"""holds the chat session class"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from .base import Base, db

if TYPE_CHECKING:
    from .chatmessage import ChatMessage
    from .user import User


class ChatSession(Base):
    """A class for chat sessions.

    inherits:
        - `Base` \n
    attributes:
        - `id (int)`: the id of the session
        - `user_id (int)`: the id of the user in the session
        - `start_timestamp (datetime)`: the time the session was started
        - `messages (list[ChatMessage])`: the messages in the session \n
    """

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    start_timestamp: Mapped[datetime] = db.Column(db.DateTime, default=datetime.utcnow)

    messages: Mapped[list["ChatMessage"]] = db.relationship(
        "ChatMessage", back_populates="session", passive_deletes=True
    )

    user: Mapped["User"] = db.relationship("User", back_populates="sessions")
