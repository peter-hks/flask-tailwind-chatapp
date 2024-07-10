"""holds the chat message class"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from .base import Base, db

if TYPE_CHECKING:
    from .chatsession import ChatSession


class ChatMessage(Base):
    """A class for chat messages.

    inherits:
        - Base \n
    attributes:
        - `id (int)`: the id of the message
        - `session_id (int)`: the id of the session the message is in
        - `user_message (str)`: the message from the user
        - `ai_message (str)`: the message from the ai
        - `timestamp (datetime)`: the time the message was sent \n
    """

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    session_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("chat_session.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_message: Mapped[str] = db.Column(db.Text, nullable=False)
    ai_message: Mapped[str] = db.Column(db.Text, nullable=False)
    timestamp: Mapped[datetime] = db.Column(db.DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = db.relationship(
        "ChatSession", back_populates="messages"
    )
