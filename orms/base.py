"""Module that stores the base class for all models and `db` instance"""

# pylint: disable=useless-super-delegation

import logging
from typing import TYPE_CHECKING, Any, ClassVar, Type

import sqlalchemy
import sqlalchemy.exc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import registry
from typing_extensions import Self, Unpack

from utils import classproperty

db = SQLAlchemy()
if TYPE_CHECKING:
    import _hint

    db: _hint._TSQLA


class Base(db.Model):
    """Base class for all models

    inherits:
        - Base
    """

    __abstract__: bool = True
    __table_name__: str
    __table__: sqlalchemy.Table

    registry: ClassVar[registry]

    @classproperty
    def primary_keys(cls: Type[Self]) -> list[str]:  # pylint: disable=no-self-argument
        """Returns a list of string columns as the primary keys for the class as a property."""

        return [key.name for key in cls.__table__.columns if key.primary_key]

    @classproperty
    def cols(cls: Type[Self]) -> list[str]:  # pylint: disable=no-self-argument
        """list of all columns"""
        return cls.__table__.columns.keys()

    @classmethod
    def from_dict(cls: Type[Self], data: dict[Unpack[Any]]) -> Self:
        """Create a new instance of the class from a dictionary

        Args:
            - `data (dict[str, Any])`: dictionary to create the instance from \n
        Returns:
            - `cls`: new instance of the class
        """
        try:
            return cls(**data)
        except TypeError:
            return cls(**data.__dict__)

    @classmethod
    def purge_all(cls: Type[Self]) -> None:
        """Purge all rows of this table from the database.

        be careful with this; you have been warned

        Args:
            - `cls (Type[Base])`: table to purge \n
        """

        with db.session.begin_nested():
            db.session.query(cls).delete()
        logging.info("Purged all instances of %s from the database", cls)

    def __init__(self, **kwargs) -> None:
        """Generic `Base` class constructor, defined only for type hinting.

        Refer to class docstring for more information

        args:
            - `**kwargs`: keyword arguments to pass to the constructor \n
        """
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """unified representation of all ORMs"""
        return f"<{self.__class__.__name__}({', '.join(f'{key}={getattr(self, key, None)}' for key in self.primary_keys)})>"  # pylint: disable=line-too-long

    def __str__(self) -> str:
        return self.__repr__()

    def insert(self) -> None:
        """Add the instance to the database"""

        with db.session.begin_nested():
            db.session.add(self)
        logging.info("Added %s to the database", self)

    def delete(self) -> None:
        """Remove the instance from the database"""

        with db.session.begin_nested():
            try:
                db.session.delete(self)
            except sqlalchemy.exc.InvalidRequestError:
                db.session.query(self.__class__).filter_by(
                    **self.as_dict(cols_only=True)
                ).delete()
        logging.info("Removed %s from the database", self)

    def upsert(self) -> None:
        """Add or update the instance in the database"""
        with db.session.begin_nested():
            db.session.merge(self)
        logging.info("Upserted %s in the database", self)

    def as_dict(self, children: bool = True, cols_only: bool = False) -> dict[str, Any]:
        """return the class as a dictionary

        args:
            - `with_children (bool)`: include children in the dict
            - `cols_only (bool)`: only include columns in the dict \n
        returns:
            - `dict[str, Any]`: dictionary representation of the class"""

        return {
            key: (
                [i.as_dict() if isinstance(i, Base) else i for i in value]
                if isinstance(value, list) and children
                else (
                    value.as_dict() if isinstance(value, Base) and children else value
                )
            )
            for key, value in self.__dict__.items()
            if not key.startswith("_") and (not cols_only or key in self.cols)
        }
