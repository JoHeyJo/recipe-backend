from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import User, db, Ingredient, Recipe, RecipeIngredient, QuantityUnit, QuantityAmount
from sqlalchemy.exc import IntegrityError
from exceptions import *

bcrypt = Bcrypt()


def highlight(value, divider):
    print(divider * 10)
    print(value)
    print(divider * 10)


class UserRepo():
    """Facilitate User table interactions"""
    @staticmethod
    def signup(user_name, first_name, last_name, email, password):
        """Sign up user. Hashes password and adds user to system. => Token"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
            is_admin=False
        )
        token = create_access_token(identity=user.user_name)
        try:
            db.session.add(user)
            db.session.commit()
            return token
        except IntegrityError as e:
            db.session.rollback()
            if "users_user_name_key" in str(e.orig):
                raise UsernameAlreadyTakenError(
                    "This username is already taken.")
            elif "users_email_key" in str(e.orig):
                raise EmailAlreadyRegisteredError(
                    "This email is already taken.")
            else:
                raise SignUpError("An error occurred during signup.")

    @staticmethod
    def authenticate(user_name, password):
        """Find user with username and password. Return False for incorrect credentials"""

        user = User.query.filter_by(user_name=user_name).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                token = create_access_token(
                    identity=user.user_name, additional_claims={"is_admin": user.is_admin})
                return token
        return False


class RecipeRepo():
    """Facilitates recipes table interactions"""
    @staticmethod
    def add_recipe(name, preparation, notes):
        """Add initial recipe information to database"""
        recipe = Recipe(name=name, preparation=preparation, notes=notes)
        try:
            db.session.add(recipe)
            db.session.commit()
            return {"recipe_title": name,
                    "recipe_id": recipe.id,
                    "preparation": preparation,
                    "notes": notes}
        except IntegrityError as e:
            db.session.rollback()
            raise {"error": "error add_recipe"}


class RecipeIngredientRepo():
    """Facilitates creation of record that corresponds to a recipe"""
    @staticmethod
    def create_recipe(recipe_id, ingredient_id, quantity_unit_id, quantity_amount_id):
        """Create recipe record"""
        # highlight(recipe_id,'*')
        # highlight(ingredient_id, '/')  # arg passed is an object {'id': None}
        # highlight(quantity_unit_id, '>')
        # highlight(quantity_amount_id, '=')
        recipe = RecipeIngredient(
            recipe_id=recipe_id, ingredient_id=ingredient_id, quantity_unit_id=quantity_unit_id, quantity_amount_id=quantity_amount_id)
        try:
            db.session.add(recipe)
            db.session.commit()
        except InterruptedError as e:
            db.rollback()
            raise {"error": "error in create_recipe"}


class QuantityUnitRepo():
    """Facilitates quantity units table interactions"""
    @staticmethod
    def add_quantity_unit(unit):
        """Add quantity unit to database"""
        value = QuantityUnit.query.filter_by(unit=unit).first()
        if value:
            return value.id

        quantity_unit = QuantityUnit(unit=unit)
        try:
            db.session.add(quantity_unit)
            return quantity_unit.id
        except InterruptedError as e:
            db.rollback()
            raise {"error": "error in add_quantity_unit"}


class QuantityAmountRepo():
    """Facilitates quantity amount table interactions"""
    @staticmethod
    def add_quantity_amount(amount):
        """Add quantity amount to database"""
        value = QuantityAmount.query.filter_by(amount=amount).first()
        if value:
            return value.id

        quantity_amount = QuantityAmount(amount=amount)
        try:
            db.session.add(quantity_amount)
            return quantity_amount.id
        except InterruptedError as e:
            db.rollback()
            raise {"error": "error in add_quantity_amount"}


class IngredientRepo():
    """Facilitates Ingredient table interactions"""
    @staticmethod
    def add_ingredient(ingredient):
        """Adds an ingredient to database"""
        try:
            value = Ingredient.query.filter_by(ingredient=ingredient).first()
            highlight(value,'@')
            if value:
                return value.id
            else:
                ingredient = Ingredient(ingredient=ingredient)
            ingredient = db.session.add(ingredient)
            highlight(ingredient,'*')
            return ingredient.id
        except InterruptedError as e:
            db.rollback()
            raise {"error": "error in IngredientRepo - add_ingredient"}


class IngredientsRepo():
    """Directs incoming data to corresponding repo methods"""
    @staticmethod
    def add_ingredients(ingredients):
        """Adds list of ingredients - calls repo methods to add ingredient components"""
        ingredients_data = []
        for ingredient in ingredients:
            ingredient_name = ingredient["ingredient"]
            quantity_amount = ingredient["quantity_amount"] or None
            quantity_unit = ingredient["quantity_unit"] or None

            try:
                # should these have individual try/catch???
                ingredient_id = IngredientRepo.add_ingredient(ingredient_name)
                highlight(ingredient_id,'8')
                if quantity_amount:
                    amount_id = QuantityAmountRepo.add_quantity_amount(
                        quantity_amount)
                if quantity_unit:
                    unit_id = QuantityUnitRepo.add_quantity_unit(quantity_unit)
                db.session.commit()

                ingredients_data.append(
                    {
                        "ingredient": ingredient["ingredient"],
                        "ingredient_id": ingredient_id,
                        "amount_id": amount_id,
                        "unit_id": unit_id
                    })

            except InterruptedError as e:
                db.rollback()
                raise {"error": "error in IngredientsRepo - add_ingredients"}
        return ingredients_data
