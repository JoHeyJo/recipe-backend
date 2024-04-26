from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT, String
from sqlalchemy.orm import Mapped, mapped_column
from annotations import str_255, str_unique_255
from mixins import TableNameMixin, TimestampMixin, ReprMixin
from typing import Optional

db = SQLAlchemy()


class User(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Users table"""

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str_255]
    last_name: Mapped[str_255]
    email: Mapped[str_unique_255]
    password: Mapped[str_255]
    user_name: Mapped[str_unique_255]
    is_admin: Mapped[bool]

class Recipe(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe table"""

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str_255]
    preparation: Mapped[str_255]
    notes: Mapped[str_255]

class 

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
