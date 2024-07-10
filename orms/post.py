"""holds the Post class"""

from datetime import datetime

from sqlalchemy.orm import Mapped

from .base import Base, db


class Post(Base):  # pylint: disable=too-few-public-methods
    """A class for posts.

    inherits:
        - Base
    attributes:
        - `id (int)`: the id of the post
        - `created (datetime)`: the time the post was created
        - `prompt (str)`: the prompt for the post
        - `user (bool)`: whether the post was made by a user
        - `context (str)`: the context of the post \n
    """

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    created: Mapped[datetime] = db.Column(db.DateTime, default=datetime.utcnow)
    prompt: Mapped[str] = db.Column(db.Text, nullable=False)
    user: Mapped[bool] = db.Column(db.Boolean, nullable=False)
    context: Mapped[str] = db.Column(db.Text)
