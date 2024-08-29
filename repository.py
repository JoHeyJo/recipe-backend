from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import *
from sqlalchemy.exc import SQLAlchemyError
from exceptions import *

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
    def create_recipe(name, preparation, notes):
        """Creates recipe instance and adds it to database"""
        recipe = Recipe(name=name, preparation=preparation, notes=notes)
        try:
            db.session.add(recipe)
            db.session.commit()
            return {"recipe_title": name,
                    "recipe_id": recipe.id,
                    "preparation": preparation,
                    "notes": notes}
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"create_recipe error:{e}")


class QuantityUnitRepo():
    """Facilitates quantity_units table interactions"""
    @staticmethod
    def create_quantity_unit(unit):
        """Create quantity unit and add to database"""
        try:
            value = QuantityUnit.query.filter_by(unit=unit).first()
            if value:
                return value.id

            quantity_unit = QuantityUnit(unit=unit)
            db.session.add(quantity_unit)
            db.session.commit()
            return {"id": quantity_unit.id, "unit": quantity_unit.unit}
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"create_quantity_unit:{e}"})

    @staticmethod
    def get_all_units():
        """Return all units"""
        try:
            units = QuantityUnit.query.all()
            return [QuantityUnit.serialize(unit) for unit in units]
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"get_all_units error: {e}"})


class QuantityAmountRepo():
    """Facilitates quantity_amounts table interactions"""
    @staticmethod
    def create_quantity_amount(amount):
        """Create quantity amount and add to database"""
        try:
            value = QuantityAmount.query.filter_by(amount=amount).first()
            if value:
                return value.id

            quantity_amount = QuantityAmount(amount=amount)
            db.session.add(quantity_amount)
            db.session.commit()
            return {"id": quantity_amount.id, "amount": quantity_amount.amount}
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"create_quantity_amount:{e}"})

    @staticmethod
    def get_all_amounts():
        """Return all amounts"""
        try:
            amounts = QuantityAmount.query.all()
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"get_all_amounts error: {e}"})


class IngredientRepo():
    """Facilitates ingredients table interactions"""

    @staticmethod
    def create_ingredient(ingredient):
        """Create ingredient and add to database"""
        try:
            value = Ingredient.query.filter_by(ingredient=ingredient).first()
            if value:
                return value.id
            else:
                ingredient = Ingredient(ingredient=ingredient)
            db.session.add(ingredient)
            db.session.commit()
            return {"id": ingredient.id, "ingredient": ingredient.ingredient}
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"create_ingredient error: {e}"})

    @staticmethod
    def get_all_ingredients():
        """Return all ingredients"""
        try:
            ingredients = Ingredient.query.all()
            return [Ingredient.serialize(ingredient) for ingredient in ingredients]
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"get_all_ingredients error: {e}"})


class IngredientsRepo():
    """Directs incoming data to corresponding repo methods"""
    @staticmethod
    def add_ingredients(ingredients):
        """Add list of ingredients to corresponding repo methods"""
        ingredients_data = []
        for ingredient in ingredients:
            ingredient_name = ingredient["ingredient"]
            quantity_amount = ingredient["quantity_amount"] or None
            quantity_unit = ingredient["quantity_unit"] or None

            try:
                ingredient_id = IngredientRepo.create_ingredient(
                    ingredient_name)
                if quantity_amount:
                    amount_id = QuantityAmountRepo.create_quantity_amount(
                        quantity_amount)
                if quantity_unit:
                    unit_id = QuantityUnitRepo.create_quantity_unit(
                        quantity_unit)

                ingredients_data.append(
                    {
                        "ingredient": ingredient["ingredient"],
                        "ingredient_id": ingredient_id,
                        "amount_id": amount_id,
                        "unit_id": unit_id
                    })

            except SQLAlchemyError as e:
                db.session.rollback()
                raise Exception({f"add_ingredients error: {e}"})
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
            db.session.rollback()
            raise Exception({f"create_book error: {e}"})


class InstructionRepo():
    """Facilitates instructions table interactions"""

    @staticmethod
    def process_instructions(instructions):
        """Directs instructions to create_instruction"""
        for instruction in instructions:
            try:
                value = Ingredient.query.get_or_404(instruction.id)
                if value:
                    return value.id
                else:
                    InstructionRepo.create_instruction(instruction=instruction)
            except SQLAlchemyError as e:
                db.session.rollback()
                raise Exception({f"create_instruction error: {e}"})

    @staticmethod
    def create_instruction(instruction):
        """Create instruction and add to database"""
        instruction = Instruction(instruction=instruction)
        try:
            db.session.add(instruction)
            db.session.commit()
            return {'id': instruction.id, 'instruction': instruction.instruction}
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"create_instruction error: {e}"})


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
            db.session.rollback()
            raise Exception({f"create_recipe error:{e}"})


class RecipeBookRepo():
    """Facilitates association of recipes & books"""
    @staticmethod
    def create_entry(book_id, recipe_id):
        """Create recipe and book association -> add to database"""
        try:
            entry = RecipeBook(book_id=book_id, recipe_id=recipe_id)
            highlight(entry, "*")
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"create_entry error:{e}"})


class UserBookRepo():
    """Facilitates association of users & books"""
    @staticmethod
    def create_entry(user_id, book_id):
        """Create recipe and book association -< add to database"""
        try:
            entry = UserBook(user_id=user_id, book_id=book_id)
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception({f"create_entry:{e}"})
