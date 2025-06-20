
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from annotations import str_255, str_unique_255, str_255_nullable, boolean
from mixins import TableNameMixin, TimestampMixin, ReprMixin, AssociationTableNameMixin
from typing import Optional, List
from utils.functions import highlight

db = SQLAlchemy()


class User(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Users table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str_255]
    last_name: Mapped[str_255]
    email: Mapped[str_unique_255]
    password: Mapped[str_255]
    user_name: Mapped[str_unique_255]
    default_book_id: Mapped[Optional[int]] = mapped_column(
        BIGINT, ForeignKey("books.id"))

    def serialize(self):
        """Serialize User table data into dict"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "user_name": self.user_name,
            "default_book_id": self.default_book_id
        }

    # recipes = db.relationship('Recipe', secondary='user_recipes', backref='users')
    ### Instead Use type annotation for better type checking and readability ###
    # recipes: Mapped[List['Recipe']] = relationship(
    #     'Recipe', secondary='user_recipes', back_populates='users')

    books: Mapped[List['Book']] = relationship(
        'Book', secondary='users_books', back_populates='users')


class Recipe(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Recipe table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str_255]
    notes: Mapped[str_255_nullable]

    def serialize(self):
        """Serialize Recipe table data into dict"""
        return {"id": self.id, "name": self.name, "notes": self.notes}

    # opens up access to data spread across multiple primary tables
    # (amounts, units, items) consolidated in Ingredient
    ingredients = relationship(
        'Ingredient', back_populates='recipe', passive_deletes=True, order_by="Ingredient.id")

    books: Mapped[List['Book']] = relationship(
        'Book', secondary='recipes_books', back_populates='recipes',
        passive_deletes=True)

    instructions: Mapped[List['Instruction']] = relationship(
        'Instruction', secondary='recipes_instructions', back_populates='recipes',
        passive_deletes=True, order_by="RecipeInstruction.id")

    units: Mapped[List['QuantityUnit']] = relationship(
        "QuantityUnit", secondary='ingredients', back_populates='recipes', viewonly=True)

    amounts: Mapped[List['QuantityAmount']] = relationship(
        "QuantityAmount", secondary='ingredients', back_populates='recipes', viewonly=True)

    items: Mapped[List['Item']] = relationship(
        "Item", secondary='ingredients', back_populates='recipes', viewonly=True)


class Book(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Book table"""
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

    amounts: Mapped[List['QuantityAmount']] = relationship(
        "QuantityAmount", secondary='amounts_books', back_populates='books')
    units: Mapped[List['QuantityUnit']] = relationship(
        "QuantityUnit", secondary='units_books', back_populates='books')
    items: Mapped[List['Item']] = relationship(
        "Item", secondary='items_books', back_populates='books')


class QuantityAmount(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Amount table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    value: Mapped[str_unique_255]

    def serialize(self):
        """Serialize amount table data into dict"""
        return {"id": self.id, "value": self.value}

    books: Mapped[List['Book']] = relationship(
        "Book", secondary='amounts_books', back_populates='amounts')

    recipes: Mapped[List['Recipe']] = relationship(
        "Recipe", secondary='ingredients', back_populates='amounts', viewonly=True)

    ingredients: Mapped[List['Ingredient']] = relationship(
        "Ingredient", back_populates='amount')


class QuantityUnit(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Quantity Unit table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    type: Mapped[str_unique_255]

    def serialize(self):
        """Serialize unit table data into dict"""
        return {"id": self.id, "type": self.type}

    books: Mapped[List['Book']] = relationship(
        "Book", secondary='units_books', back_populates='units')

    recipes: Mapped[List['Recipe']] = relationship(
        "Recipe", secondary='ingredients', back_populates='units', viewonly=True)

    ingredients: Mapped[List['Ingredient']] = relationship(
        "Ingredient", back_populates='unit')


class Item(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Item table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str_unique_255]

    def serialize(self):
        """Serialize amount table data into dict"""
        return {"id": self.id, "name": self.name}

    books: Mapped[List['Book']] = relationship(
        "Book", secondary='items_books', back_populates='items')

    recipes: Mapped[List['Recipe']] = relationship(
        "Recipe", secondary='ingredients', back_populates='items', viewonly=True)

    ingredients: Mapped[List['Ingredient']] = relationship(
        "Ingredient", back_populates='item')


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

    # recipe_instruction: Mapped['RecipeInstruction'] = relationship(
    #     "RecipeInstruction", backref="instructions", uselist=False
    # )

###################### ASSOCIATION MODELS ############################


class Ingredient(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Enhanced association table for recipes and [amounts, units, items] - Allows 
    queries of whole ingredient instances and their individual parts 
    e.g. item, amount, unit"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        'recipes.id', ondelete="CASCADE"), nullable=False)
    quantity_amount_id: Mapped[int] = mapped_column(Integer, ForeignKey('quantity_amounts.id'), nullable=True)
    quantity_unit_id: Mapped[int] = mapped_column(Integer, ForeignKey('quantity_units.id'), nullable=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('items.id'), nullable=False)

    # enhanced association table attributes
    # Does ORM delete work with passive_deletes=True?????
    amount: Mapped['QuantityAmount'] = relationship(
        "QuantityAmount", back_populates="ingredients")
    unit: Mapped['QuantityUnit'] = relationship(
        "QuantityUnit", back_populates="ingredients")
    item: Mapped['Item'] = relationship("Item", back_populates="ingredients")
    recipe: Mapped['Recipe'] = relationship(
        "Recipe", back_populates="ingredients")


class RecipeBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for books and recipes"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"))
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"))


class UserBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for users and books"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))


class BookInstruction(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for books and instructions"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"))
    instruction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("instructions.id"))


class RecipeInstruction(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for recipes and instructions"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    instruction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("instructions.id"))


class AmountBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for amounts and books"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    amount_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quantity_amounts.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"))


class UnitBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for unit and books"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quantity_units.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"))


class ItemBook(ReprMixin, AssociationTableNameMixin, TimestampMixin, db.Model):
    """Association table for items and books"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"))


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        try:
            # db.drop_all()
            db.create_all()
        except Exception as e:
            print(f"Error creating database tables: {e}")