from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import *
from sqlalchemy.exc import SQLAlchemyError
from exceptions import *
import logging

bcrypt = Bcrypt()


def highlight(value, divider):
    print(divider * 10)
    print(value)
    print(divider * 10)


class UserRepo():
    """Facilitate users table interactions"""
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
        except SQLAlchemyError as e:
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
    def create_recipe(name, notes):
        """Creates recipe instance and adds it to database"""
        recipe = Recipe(name=name, notes=notes)
        try:
            db.session.add(recipe)
            db.session.commit()
            return {"recipe_title": name,
                    "recipe_id": recipe.id,
                    "notes": notes}
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_recipe error:{e}")


class QuantityUnitRepo():
    """Facilitates quantity_units table interactions"""
    @staticmethod
    def process_quantity_unit(unit):
        """Creates and returns new unit or returns existing unit"""
        is_stored = unit.get("id")
        if is_stored:
            return unit
        else:
            return QuantityUnitRepo.create_quantity_unit(unit=unit["type"])

    @staticmethod
    def create_quantity_unit(unit):
        """Create quantity unit and add to database"""
        try:
            highlight(unit,"$")
            quantity_unit = QuantityUnit(unit=unit)
            db.session.add(quantity_unit)
            db.session.commit()
            return {"id": quantity_unit.id, "unit": quantity_unit.unit}
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_quantity_unit:{e}")

    @staticmethod
    def get_all_units():
        """Return all units"""
        try:
            units = QuantityUnit.query.all()
            return [QuantityUnit.serialize(unit) for unit in units]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"get_all_units error: {e}")


class QuantityAmountRepo():
    """Process amounts & facilitates quantity_amounts table interactions"""
    @staticmethod
    def process_amount(amount):
        """Creates and returns new amount or return existing amount """
        is_stored = amount.get("id")
        if is_stored:
            return amount
        else:
            return QuantityAmountRepo.create_amount(amount=amount["value"])

    @staticmethod
    def create_amount(amount):
        """Create quantity amount and add to database"""
        try:
            quantity_amount = QuantityAmount(amount=amount)
            db.session.add(quantity_amount)
            db.session.commit()
            return {"id": quantity_amount.id, "amount": quantity_amount.amount}
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_amount:{e}")

    @staticmethod
    def get_all_amounts():
        """Return all amounts"""
        try:
            amounts = QuantityAmount.query.all()
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"get_all_amounts error: {e}")


class IngredientRepo():
    """Processes ingredients & facilitates table interactions"""
    @staticmethod
    def process_ingredient(ingredient):
        """Create and returns new ingredient or returns existing ingredient"""
        is_stored = ingredient.get("id")
        if is_stored:
            return ingredient
        else:
            return IngredientRepo.create_ingredient(ingredient=ingredient["name"])

    @staticmethod
    def create_ingredient(ingredient):
        """Create ingredient and add to database"""
        try:
            ingredient = Ingredient(ingredient=ingredient)
            db.session.add(ingredient)
            db.session.commit()
            return {"id": ingredient.id, "ingredient": ingredient.ingredient}
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_ingredient error: {e}")

    @staticmethod
    def get_all_ingredients():
        """Return all ingredients"""
        try:
            ingredients = Ingredient.query.all()
            return [Ingredient.serialize(ingredient) for ingredient in ingredients]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"get_all_ingredients error: {e}")


class IngredientsRepo():
    """Directs incoming data to corresponding repo methods"""
    @staticmethod
    def process_ingredients(ingredients):
        """Separate ingredient components - call corresponding repo methods"""
        ingredients_data = []
        for i in ingredients:
            ingredient = i["ingredient"]
            amount = i["amount"]
            unit = i["unit"]
            try:
                ingredient = IngredientRepo.process_ingredient(ingredient=ingredient)
                if amount:
                    amount = QuantityAmountRepo.process_amount(amount=amount)
                if unit:
                    unit = QuantityUnitRepo.process_quantity_unit(unit=unit)

                ingredients_data.append(
                    {
                        # "ingredient": ingredient_name,
                        "ingredient": ingredient,
                        "amount": amount,
                        "unit": unit
                    })

            except SQLAlchemyError as e:
                highlight(e, "!")
                db.session.rollback()
                raise Exception(f"add_ingredients error: {e}")
        return ingredients_data


class BookRepo():
    """Facilitates books table interactions"""
    @staticmethod
    def create_book(title):
        """Create book title and add to database"""
        book = Book(title=title)
        try:
            db.session.add(book)
            db.session.commit()
            return {'id': book.id, 'title': book.title}
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_book error: {e}")


class InstructionRepo():
    """Facilitates instructions table interactions"""
    @staticmethod
    def process_instructions(instructions):
        """Consolidates existing instruction object with newly created instruction"""
        processed_instructions = []
        for instruction in instructions:
            is_stored = instruction.get("id")
            if is_stored:
                processed_instructions.append(instruction)
            else:
                processed_instructions.append(
                    InstructionRepo.create_instruction(instruction=instruction["instruction"]))
        return processed_instructions

    @staticmethod
    def create_instruction(instruction):
        """Create instruction and add to database"""
        try:
            instruction = Instruction(instruction=instruction)
            db.session.add(instruction)
            db.session.commit()
            return {'id': instruction.id, 'instruction': instruction.instruction}
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_instruction error: {e}")


###################### ASSOCIATION TABLES ############################


class RecipeIngredientRepo():
    """Facilitates association of recipes & ingredients """
    @staticmethod
    def create_recipe(recipe_id, ingredient_id, quantity_unit_id, quantity_amount_id):
        """Create recipe and ingredient association -> add to database"""
        entry = RecipeIngredient(
            recipe_id=recipe_id, ingredient_id=ingredient_id, quantity_unit_id=quantity_unit_id, quantity_amount_id=quantity_amount_id)
        try:
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"RecipeIngredientRepo-create_recipe error:{e}")


class RecipeBookRepo():
    """Facilitates association of recipes & books"""
    @staticmethod
    def create_entry(book_id, recipe_id):
        """Create recipe and book association -> add to database"""
        try:
            highlight(book_id, "^")
            highlight(recipe_id, "^")
            entry = RecipeBook(book_id=book_id, recipe_id=recipe_id)
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"RecipeBookRep-create_entry error:{e}")


class UserBookRepo():
    """Facilitates association of users & books"""
    @staticmethod
    def create_entry(user_id, book_id):
        """Create user and book association -> add to database"""
        try:
            entry = UserBook(user_id=user_id, book_id=book_id)
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"UserBookRepo-create_entry:{e}")


class BookInstructionRepo():
    """Facilitates association of books & instructions"""
    @staticmethod
    def create_entry(book_id, instruction_id):
        """Create book and instruction association -> add to database"""
        try:
            entry = BookInstruction(
                book_id=book_id, instruction_id=instruction_id)
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"BookInstructionRepo-create_entry:{e}")