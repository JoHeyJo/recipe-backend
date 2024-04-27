from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    children: Mapped[List["QuantityAmount"]] = relationship(
        secondary="RecipeIngredient")



class RecipeIngredient(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe Ingredient table"""
    
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(Integer,ForeignKey(recipes.recipe_id, ondelete="CASCADE"),primary_key=True)
    Column("left_id", ForeignKey("left_table.id")),
    Column("right_id", ForeignKey("right_table.id")),


class QuantityUnit(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Unit table"""

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    unit: Mapped[str_unique_255]


class QuantityAmount(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Amount table"""

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    unit: Mapped[str_unique_255]


class Ingredient(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Ingredient table"""

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    unit: Mapped[str_unique_255]
    



def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
