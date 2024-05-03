from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT, String, Integer, Column, ForeignKey
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
    ingredients = relationship('RecipeIngredient', back_populates='recipe')


class RecipeIngredient(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe Ingredient table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    quantity_unit_id = Column(Integer, ForeignKey('quantity_units.id'))
    quantity_amount_id = Column(Integer, ForeignKey('quantity_amounts.id'))

    recipe = relationship('Recipe', back_populates='ingredients')
    ingredient = relationship(
        'Ingredient', back_populates='recipe_ingredients')
    quantity_unit = relationship('QuantityUnit')
    quantity_amount = relationship('QuantityAmount')


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
    recipe_ingredients = relationship(
        'RecipeIngredient', back_populates='ingredient')
    



def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
