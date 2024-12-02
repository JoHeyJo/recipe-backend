from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import User, db, Recipe, QuantityUnit, QuantityAmount, Item, Book, Instruction, RecipeIngredient, RecipeBook, UserBook, BookInstruction, RecipeInstruction
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
        try:
            user = User(
                user_name=user_name,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_pwd,
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            token = create_access_token(identity=user.id)
            return token
        except SQLAlchemyError as e:
            highlight(e, "!")
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
                token = create_access_token(identity=user.id)
                return token
        return False
    
    @staticmethod
    def fetch_user(user_id):
        """Fetch user with corresponding id"""
        try:
            user = User.query.get(user_id)
            return User.serialize(user)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"UserRepo -> fetch_user error:{e}")

class RecipeRepo():
    """Facilitates recipes table interactions"""
    @staticmethod
    def create_recipe(name, notes):
        """Creates recipe instance and adds it to database"""
        highlight(notes, "create_recipe")
        recipe = Recipe(name=name, notes=notes)
        highlight(recipe.notes,"instantiated")
        try:
            db.session.add(recipe)
            db.session.commit()
            return Recipe.serialize(recipe)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_recipe error:{e}")
    
    @staticmethod
    def fetch_recipes(user_id, book_id):
        """Retrieve recipes corresponding to user's book"""
        try:
            book = Book.query.get(book_id)
            recipes = book.recipes
            return [Recipe.serialize(recipe) for recipe in recipes]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_recipe error:{e}")
        
    @staticmethod
    def delete_recipe(recipe_id):
        """Deletes recipe and all references in association tables"""
        try:
            recipe = Recipe.query.get(recipe_id)
            db.session.delete(recipe)
            db.session.commit()
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"delete_recipe error:{e}")


class QuantityUnitRepo():
    """Facilitates quantity_units table interactions"""
    @staticmethod
    def process_unit(unit):
        """Creates and returns new unit or returns existing unit"""
        is_stored = unit.get("id")
        if is_stored is not None:
            return unit
        else:
            return QuantityUnitRepo.create_unit(type=unit["type"])

    @staticmethod
    def create_unit(type):
        """Create quantity unit and add to database"""
        try:
            quantity_unit = QuantityUnit(type=type)
            db.session.add(quantity_unit)
            db.session.commit()
            return QuantityUnit.serialize(quantity_unit)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_unit:{e}")

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
        if is_stored is not None:
            return amount
        else:
            return QuantityAmountRepo.create_amount(value=amount["value"])

    @staticmethod
    def create_amount(value):
        """Create quantity amount and add to database"""
        try:
            quantity_amount = QuantityAmount(value=value)
            db.session.add(quantity_amount)
            db.session.commit()
            return QuantityAmount.serialize(quantity_amount)
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


class ItemRepo():
    """Processes item & facilitates table interactions"""
    @staticmethod
    def process_item(item):
        """Create and returns new item or returns existing item"""
        is_stored = item.get("id")
        if is_stored is not None:
            return item
        else:
            return ItemRepo.create_item(name=item["name"])

    @staticmethod
    def create_item(name):
        """Create item and add to database"""
        try:
            item = Item(name=name)
            db.session.add(item)
            db.session.commit()
            return Item.serialize(item)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_item error: {e}")

    @staticmethod
    def get_all_items():
        """Return all items"""
        try:
            items = Item.query.all()
            return [Item.serialize(item) for item in items]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"get_all_item error: {e}")


class IngredientsRepo():
    """Directs incoming data to corresponding repo methods"""
    @staticmethod
    def process_ingredients(ingredients):
        """Separate ingredient components - call corresponding repo methods"""
        ingredients_data = []
        for ingredient in ingredients:
            item = ingredient["item"]
            amount = ingredient["amount"]
            unit = ingredient["unit"]
            try:
                item = ItemRepo.process_item(item=item)
                if amount:
                    amount = QuantityAmountRepo.process_amount(amount=amount)
                if unit:
                    unit = QuantityUnitRepo.process_unit(unit=unit)

                ingredients_data.append(
                    {
                        "item": item,
                        "amount": amount,
                        "unit": unit
                    })

            except SQLAlchemyError as e:
                highlight(e, "!")
                db.session.rollback()
                raise Exception(
                    f"IngredientsRepo -> process_ingredients error: {e}")
        return ingredients_data

    @staticmethod
    def build_ingredients(instance):
        """Build ingredient from corresponding instances(Recipe)"""
        ingredients = []
        for ingredient in instance.ingredients:
            amount = QuantityAmount.serialize(ingredient.amount)
            unit = QuantityUnit.serialize(ingredient.unit)
            item = Item.serialize(ingredient.item)
            ingredients.append({"ingredient_id": ingredient.id, "amount": amount, "unit": unit, "item": item})
        return ingredients


class BookRepo():
    """Facilitates books table interactions"""
    @staticmethod
    def create_book(title, description):
        """Create book and add to database"""
        book = Book(title=title, description=description)
        try:
            db.session.add(book)
            db.session.commit()
            return Book.serialize(book)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"create_book error: {e}")
    
    @staticmethod
    def get_user_books(user_id):
        """Returns all books associated to user"""
        try:
            user = User.query.get(user_id)
            return [book.id for book in user.books]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"BookRepo - get_user_books error: {e}")
        

class InstructionRepo():
    """Facilitates instructions table interactions"""
    @staticmethod
    def process_instructions(instructions):
        """Consolidates existing instruction object with newly created instruction"""
        processed_instructions = []
        for instruction in instructions:
            is_stored = instruction.get("id")
            if is_stored is not None:
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
            return Instruction.serialize(instruction)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"InstructionRepo - create_instruction error: {e}")

    @staticmethod
    def get_instructions():
        """Return all instructions"""
        try:
            instructions = Instruction.query.all()
            return [Instruction.serialize(instruction) for instruction in instructions]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"InstructionRepo - get_instruction error: {e}")
        
    @staticmethod
    def build_instructions(instances):
        """Return all associated instructions from recipe instance and join with 
        recipe_instruction identifier"""
        highlight(instances, "%")
        instructions = []
        if not instances:
            return [] 
        for instruction_instance in instances:
            instruction = Instruction.serialize(instruction_instance)
            # inject PK from recipes_instructions association table
            association_id = instruction_instance.recipe_instruction.id
            instruction["association_id"] = association_id
            instructions.append(instruction)
        return instructions


###################### ASSOCIATION TABLES ############################


class RecipeIngredientRepo():
    """Facilitates association of recipes & ingredients"""
    @staticmethod
    def create_ingredient(recipe_id, item_id, quantity_unit_id, quantity_amount_id):
        """Create recipe and ingredient association -> add to database"""
        entry = RecipeIngredient(
            recipe_id=recipe_id, item_id=item_id, quantity_unit_id=quantity_unit_id, quantity_amount_id=quantity_amount_id)
        try:
            db.session.add(entry)
            db.session.commit()
            return entry.id
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"RecipeIngredientRepo-create_ingredient error:{e}")


class RecipeBookRepo():
    """Facilitates association of recipes & books"""
    @staticmethod
    def create_entry(book_id, recipe_id):
        """Create recipe and book association -> add to database"""
        try:
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

class RecipeInstructionRepo():
    """Facilitates association of recipes & instructions"""
    @staticmethod
    def create_entry(recipe_id, instruction_id):
        """Create recipe and instruction association -> add to database"""
        try:
            entry = RecipeInstruction(recipe_id=recipe_id, instruction_id=instruction_id)
            db.session.add(entry)
            db.session.commit()
            return entry.id
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"RecipeInstructionRepo-create_entry:{e}")
