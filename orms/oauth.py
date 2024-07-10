"""oauth model"""

from typing import TYPE_CHECKING

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm import Mapped

from .base import Base, db

if TYPE_CHECKING:
    from .user import User


class OAuth(OAuthConsumerMixin, Base):
    """oauth class"""

    provider_user_id: Mapped[str] = db.Column(
        db.String(256), unique=True, nullable=False
    )
    user_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )

    user: Mapped["User"] = db.relationship(
        "User", back_populates="oauth", passive_deletes=True
    )
