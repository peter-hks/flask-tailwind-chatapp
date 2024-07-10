"""module to typehint this stupid `db` object from `flask_sqlalchemy`"""

import sqlalchemy
import sqlalchemy.event
import sqlalchemy.exc
import sqlalchemy.orm
import sqlalchemy.types
import sqlalchemy.util
from flask_sqlalchemy import SQLAlchemy


class _TSQLA(SQLAlchemy):
    """internal class for type hinting \
            this DOES NOT get imported OR used

        inherits:
            - SQLAlchemy
        """

    Column = sqlalchemy.Column
    Text = sqlalchemy.Text
    Integer = sqlalchemy.Integer
    String = sqlalchemy.String
    ForeignKey = sqlalchemy.ForeignKey
    DateTime = sqlalchemy.DateTime
    Boolean = sqlalchemy.Boolean
    Float = sqlalchemy.Float
    JSON = sqlalchemy.JSON
    BigInteger = sqlalchemy.BigInteger
    Date = sqlalchemy.Date
    SmallInteger = sqlalchemy.SmallInteger
    LargeBinary = sqlalchemy.LargeBinary
    Numeric = sqlalchemy.Numeric
    Time = sqlalchemy.Time
    DateTime = sqlalchemy.DateTime
    DECIMAL = sqlalchemy.DECIMAL
    ARRAY = sqlalchemy.ARRAY
    # JSONB = sqlalchemy.JSONB
    Enum = sqlalchemy.Enum
    UniqueConstraint = sqlalchemy.UniqueConstraint
    Index = sqlalchemy.Index
    CheckConstraint = sqlalchemy.CheckConstraint
    ForeignKeyConstraint = sqlalchemy.ForeignKeyConstraint
    Sequence = sqlalchemy.Sequence
    Table = sqlalchemy.Table
    MetaData = sqlalchemy.MetaData
    event = sqlalchemy.event
    exc = sqlalchemy.exc
    orm = sqlalchemy.orm
    types = sqlalchemy.types
    util = sqlalchemy.util
    inspect = sqlalchemy.inspect
    schema = sqlalchemy.schema
    sql = sqlalchemy.sql
    func = sqlalchemy.func
