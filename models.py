from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from annotations import str_255
from mixins import TableNameMixin, TimestampMixin

db = SQLAlchemy()

class User(db.Model, TableNameMixin, TimestampMixin):
    """Users table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str_255]
    last_name: Mapped[str_255]
    email: Mapped[str_255]
    password: Mapped[str_255]
    user_name: Mapped[str_255]


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
