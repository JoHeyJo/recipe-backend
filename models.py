from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT, String, Integer, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from annotations import str_255, str_unique_255, str_255_nullable
from mixins import TableNameMixin, TimestampMixin, ReprMixin, AssociationTableNameMixin
from typing import Optional, List

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

    # recipes = db.relationship('Recipe', secondary='user_recipes', backref='users')
    ### Instead Use type annotation for better type checking and readability ###
    # recipes: Mapped[List['Recipe']] = relationship(
    #     'Recipe', secondary='user_recipes', back_populates='users')
    user_books: Mapped[List['Book']] = relationship(
        'Book', secondary='users_books', back_populates='users')


class Recipe(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str_255]
    preparation: Mapped[str_255_nullable]
    notes: Mapped[str_255_nullable]

    ingredients: Mapped[List['Recipe']] = relationship(
        'Ingredient', secondary='recipes_ingredients', back_populates='recipes')

    recipe_books: Mapped[List['Book']] = relationship(
        'Book', secondary='recipes_books', back_populates='recipes')


class RecipeIngredient(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for recipes and ingredients"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    recipe_id: Mapped[int] = Column(Integer, ForeignKey('recipes.id'))
    ingredient_id: Mapped[int] = Column(Integer, ForeignKey('ingredients.id'))
    quantity_unit_id: Mapped[int] = Column(Integer, ForeignKey('quantity_units.id'))
    quantity_amount_id: Mapped[int] = Column(Integer, ForeignKey('quantity_amounts.id'))


class QuantityUnit(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Unit table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    unit: Mapped[str_unique_255]


class QuantityAmount(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Amount table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    amount: Mapped[str_unique_255]


class Ingredient(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Ingredient table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    ingredient: Mapped[str_unique_255]

    recipes: Mapped[List['Ingredient']] = relationship(
        'Recipe', secondary='recipe_ingredients', back_populates='ingredients')


class Book(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe book table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    title: Mapped[str_255]

    users: Mapped[List['User']] = relationship(
        'User', secondary='users_books', back_populates='recipes_books')


class RecipeBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for books and recipes"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = Column(Integer, ForeignKey("recipes_books.id"))
    recipe_id: Mapped[int] = Column(Integer, ForeignKey("recipes.id"))


class UserBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for users and books"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = Column(Integer, ForeignKey("recipes_books.id"))
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
