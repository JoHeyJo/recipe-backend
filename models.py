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

class Ingredient(ReprMixin, TableNameMixin, TimestampMixin, db.Model):
    """Ingredients table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()


# Ingredients
# ingredient_id(Primary Key): A unique identifier for each ingredient.
# name(Unique): The name of the ingredient. This field should have a unique constraint to prevent duplicates.
# Other columns as needed(like description, allergens, calories, etc.).
# 2. Recipes Table
# This table will store information about each recipe:

# Recipes
# recipe_id(Primary Key): A unique identifier for each recipe.
# title: The name or title of the recipe.
# description: Detailed description or instructions.
# Other relevant fields such as cooking_time, serving_size, etc.
# 3. RecipeIngredients Table(Many-to-Many)
# This junction table will link ingredients to recipes and handle the many-to-many relationship:

# RecipeIngredients
# recipe_id(Foreign Key): References recipe_id in the Recipes table.
# ingredient_id(Foreign Key): References ingredient_id in the Ingredients table.
# quantity: The amount of each ingredient needed in the recipe(e.g., "1 cup", "100 grams").
# Optionally, other specifics related to how the ingredient is used in the recipe(like preparation details, such as chopped, diced, etc.).
