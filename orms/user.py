"""This module contains the User class."""

from typing import TYPE_CHECKING, ClassVar

from flask_login import UserMixin, login_user
from sqlalchemy.orm import Mapped
from typing_extensions import Self

from .base import Base, db

if TYPE_CHECKING:
    from .chatsession import ChatSession
    from .oauth import OAuth


class User(UserMixin, Base):
    """a class for users.\n

    Inherits:
        - UserMixin
        - Base \n
    Attributes:
        - `id (int)`: the id of the user
        - `name (str)`: the name of the user
        - `avatar_url (str)`: the url of the user's avatar
        - `role (str)`: the role of the user \n
    """

    is_authenticated: ClassVar[bool]
    is_active: ClassVar[bool]
    is_anonymous: ClassVar[bool]

    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = db.Column(db.String(80), nullable=False)
    # avatar_url: Mapped[str] = db.Column(db.String(256), default="")
    job_title: Mapped[str] = db.Column(db.String)
    role: Mapped[str] = db.Column(db.String(80), default="user")
    email: Mapped[str] = db.Column(db.String(80), default="email")

    sessions: Mapped[list["ChatSession"]] = db.relationship(
        "ChatSession", back_populates="user", passive_deletes=True
    )
    oauth: Mapped["OAuth"] = db.relationship("OAuth", back_populates="user")

    @classmethod
    def from_oauth_info(cls: type[Self], data: dict[str], **remap) -> Self:
        """Create a new user from an OAuth object.

        Args:
            - `data (dict)`: the data to create the user from
            - `**remap (dict)`: remap kwargs \n
        Returns:
            - `User`: the new user
        """
        columns = cls.__table__.columns.keys()
        data.pop("id", None)
        for key, value in data.copy().items():
            if key in remap:
                data[remap[key]] = value

        return cls.from_dict({k: v for k, v in data.items() if k in columns})

    @property
    def is_admin(self) -> bool:
        """check if the user is an admin.

        Returns:
            - `bool`: True if the user is an admin, False otherwise.
        """
        return self.role == "admin"

    def login(self, **kwargs) -> None:
        """Log the user in.

        args:
            - `**kwargs`: keyword arguments to pass to `login_user()` \n
        kwargs:
            - `remember (bool, False)`: whether to remember the user \n
            - `duration (datetime.timedelta, None)`: the duration to remember the user \n
            - `force (bool, False)`: whether to force the user to login \n
            - `fresh (bool, True)`: uses a fresh session \n
        """

        login_user(self, **kwargs)
