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
    book_id: Mapped[Optional[int]] = mapped_column(
        BIGINT, ForeignKey("books.id"))

    # recipes = db.relationship('Recipe', secondary='user_recipes', backref='users')
    ### Instead Use type annotation for better type checking and readability ###
    # recipes: Mapped[List['Recipe']] = relationship(
    #     'Recipe', secondary='user_recipes', back_populates='users')
    books: Mapped[List['Book']] = relationship(
        'Book', secondary='users_books', back_populates='users')

    def serialize(self):
        """Serialize User table data into dict"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "user_name": self.user_name,
            "book_id": self.book_id
        }


class Recipe(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str_255]
    notes: Mapped[str_255_nullable]

    ingredients: Mapped[List['RecipeIngredient']] = relationship(
        'RecipeIngredient', backref='recipe')

    books: Mapped[List['Book']] = relationship(
        'Book', secondary='recipes_books', back_populates='recipes')
    
    instructions: Mapped[List['Instruction']] = relationship(
        'Instruction', secondary='recipes_instructions', back_populates='recipes'
    )

    def serialize(self):
        """Serialize Recipe table data into dict"""
        return {"id": self.id, "name": self.name, "notes": self.notes}


class QuantityUnit(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Unit table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    type: Mapped[str_unique_255]

    def serialize(self):
        """Serialize unit table data into dict"""
        return {"id": self.id, "type": self.type}


class QuantityAmount(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Amount table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    value: Mapped[str_unique_255]

    def serialize(self):
        """Serialize amount table data into dict"""
        return {"id": self.id, "value": self.value}


class Item(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Item table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str_unique_255]

    def serialize(self):
        """Serialize amount table data into dict"""
        return {"id": self.id, "name": self.name}

class Book(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe book table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    title: Mapped[str_255]
    description: Mapped[str_255]

    def serialize(self):
        """Serialize Book table data into dict"""
        return {"id": self.id, "title": self.title, "description": self.description}

    users: Mapped[List['User']] = relationship(
        'User', secondary='users_books', back_populates='books')

    recipes: Mapped[List['Recipe']] = relationship(
        'Recipe', secondary='recipes_books', back_populates='books')

    instructions: Mapped[List['Instruction']] = relationship(
        "Instruction", secondary='books_instructions', back_populates='books')


class Instruction(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Instruction table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    instruction: Mapped[str_255]

    def serialize(self):
        """Serialize instruction table data into dict"""
        return {"id": self.id, "instruction": self.instruction}

    books: Mapped[List['Book']] = relationship(
        'Book', secondary="books_instructions", back_populates="instructions")
    
    recipes: Mapped[List['Recipe']] = relationship(
        "Recipe", secondary="recipes_instructions", back_populates="instructions"
    )


###################### ASSOCIATION MODELS ############################


class RecipeIngredient(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for recipes and ingredients"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    recipe_id: Mapped[int] = Column(Integer, ForeignKey('recipes.id'))
    item_id: Mapped[int] = Column(Integer, ForeignKey('items.id'))
    quantity_unit_id: Mapped[int] = Column(
        Integer, ForeignKey('quantity_units.id'))
    quantity_amount_id: Mapped[int] = Column(
        Integer, ForeignKey('quantity_amounts.id'))


class RecipeBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for books and recipes"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = Column(Integer, ForeignKey("books.id"))
    recipe_id: Mapped[int] = Column(Integer, ForeignKey("recipes.id"))


class UserBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for users and books"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = Column(Integer, ForeignKey("books.id"))
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))


class BookInstruction(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for books and instructions"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = Column(Integer, ForeignKey("books.id"))
    instruction_id: Mapped[int] = Column(Integer, ForeignKey("instructions.id"))
    

class RecipeInstruction(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for books and instructions"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    recipe_id: Mapped[int] = Column(Integer, ForeignKey("recipes.id"))
    instruction_id: Mapped[int] = Column(Integer, ForeignKey("instructions.id"))


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        # db.drop_all()
        db.create_all()
