from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import User, db, Recipe, QuantityUnit, QuantityAmount, Item, Book, Instruction, Ingredient, RecipeBook, UserBook, BookInstruction, RecipeInstruction, AmountBook, UnitBook, ItemBook
from sqlalchemy.exc import SQLAlchemyError
from exceptions import *
from sqlalchemy.dialects.postgresql import insert
from utils.functions import insert_first

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
            db.session.flush()
            token = create_access_token(identity=user.id)
            return token
        except SQLAlchemyError as e:
            if "users_user_name_key" in str(e.orig):
                raise UsernameAlreadyTakenError(
                    "This username is already taken.")
            elif "users_email_key" in str(e.orig):
                raise EmailAlreadyRegisteredError(
                    "This email is already taken.")
            else:
                raise SignUpError("An error occurred during signup.")

    @staticmethod
    def login(user_name, password):
        """Find user with username and password. Return False for incorrect credentials"""

        user = User.query.filter_by(user_name=user_name).first()
        # If user exists AND user is authorized 
        if user and bcrypt.check_password_hash(user.password, password):
            return create_access_token(identity=user.id)
        return False

    @staticmethod
    def query_user(user_id):
        """Query user corresponding with id"""
        try:
            user = User.query.get(user_id)
            if user is None:
                return None 
            return user
        except SQLAlchemyError as e:
            raise Exception(f"UserRepo -> query_user error:{e}")


class RecipeRepo():
    """Facilitates recipes table interactions"""
    @staticmethod
    def create_recipe(name, notes):
        """Creates recipe instance and adds it to database"""
        recipe = Recipe(name=name, notes=notes)
        try:
            db.session.add(recipe)
            db.session.flush()
            return Recipe.serialize(recipe)
        except SQLAlchemyError as e:
            raise RuntimeError(f"create_recipe error:{e}") from e

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
            db.session.execute(
                # ✅ Use direct SQLAlchemy delete
                db.delete(Recipe).where(Recipe.id == int(recipe_id))
            )
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"delete_recipe error:{e}")


class QuantityAmountRepo():
    """Process amounts & facilitates quantity_amounts table interactions"""
    @staticmethod
    def create_amount(value):
        """Create quantity amount and add to database."""
        try:
            quantity_amount = insert_first(
                Model=QuantityAmount, data=value, column_name="value", db=db)
            return QuantityAmount.serialize(quantity_amount)
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"QuantityAmountRepo - create_amount error:{e}")

    @staticmethod
    def get_all_amounts():
        """Return all amounts"""
        try:
            amounts = QuantityAmount.query.all()
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"QuantityAmountRepo -  get_all_amounts error: {e}")

    @staticmethod
    def get_book_amounts(book_id):
        """Return user amounts"""
        try:
            amounts = Book.query.get(book_id).amounts
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"QuantityAmountRepo -  get_book_amounts error: {e}")

    @staticmethod
    def query_user_amounts(user_id):
        """Return user amounts"""
        try:
            amounts = db.session.query(QuantityAmount).join(
                AmountBook, QuantityAmount.id == AmountBook.amount_id
            ).join(
                UserBook, AmountBook.book_id == UserBook.book_id
            ).filter(UserBook.user_id == user_id).all()
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"QuantityAmountRepo - get_user_amounts error: {e}")


class QuantityUnitRepo():
    """Facilitates quantity_units table interactions"""
    @staticmethod
    def create_unit(type):
        """Create quantity unit and add to database"""
        try:
            quantity_unit = insert_first(
                Model=QuantityUnit, data=type, column_name="type", db=db)
            return QuantityUnit.serialize(quantity_unit)
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"QuantityUnitRepo - create_unit:{e}")

    @staticmethod
    def query_user_units(user_id):
        """Return user's units"""
        try:
            units = db.session.query(QuantityUnit).join(
                UnitBook, QuantityUnit.id == UnitBook.unit_id
            ).join(
                UserBook, UnitBook.book_id == UserBook.book_id
            ).filter(UserBook.user_id == user_id).all()
            return [QuantityUnit.serialize(unit) for unit in units]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"QuantityUnitRepo - get_all_units error: {e}")

    @staticmethod
    def get_book_units(book_id):
        """Return book's units"""
        try:
            units = Book.query.get(book_id).units
            return [QuantityUnit.serialize(unit) for unit in units]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"QuantityUnitRepo - get_book_units error: {e}")


class ItemRepo():
    """Processes item & facilitates table interactions"""
    @staticmethod
    def create_item(name):
        """Create item and add to database"""
        try:
            item = insert_first(
                Model=Item, data=name, column_name="name", db=db)
            return Item.serialize(item)
        except SQLAlchemyError as e:
            raise RuntimeError(f"ItemRepo - create_item error: {e}") from e

    @staticmethod
    def query_all_items():
        """Return all items"""
        try:
            items = Item.query.all()
            return [Item.serialize(item) for item in items]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"get_all_item error: {e}")

    @staticmethod
    def get_book_items(book_id):
        """Return book's items"""
        try:
            items = Book.query.get(book_id).items
            return [Item.serialize(item) for item in items]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"get_book_items error: {e}")

    @staticmethod
    def query_user_items(user_id):
        """Return user's items"""
        try:
            items = db.session.query(Item).join(
                ItemBook, Item.id == ItemBook.item_id
            ).join(
                UserBook, ItemBook.book_id == UserBook.book_id
            ).filter(UserBook.user_id == user_id).all()
            return [Item.serialize(item) for item in items]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"query_user_items error: {e}")


class IngredientsRepo():
    """Directs incoming data to corresponding repo methods"""

class BookRepo():
    """Facilitates books table interactions"""
    @staticmethod
    def create_book(title, description):
        """Create book and add to database"""
        book = Book(title=title, description=description)
        try:
            db.session.add(book)
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
            return [Book.serialize(book) for book in user.books]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"BookRepo - get_user_books error: {e}")


class InstructionRepo():
    """Facilitates instructions table interactions"""
    @staticmethod
    def create_instruction(instruction, book_id):
        """Create and add instruction to database"""
        try:
            instruction = Instruction(instruction=instruction)
            db.session.add(instruction)
            db.session.flush()
            return Instruction.serialize(instruction)
        except SQLAlchemyError as e:
            highlight(e, "!")
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
    def query_user_instructions(user_id):
        """Query all instructions associated with a user - relying on table join"""
        try:
            instructions = db.session.query(Instruction).join(
                BookInstruction, Instruction.id == BookInstruction.instruction_id
            ).join(
                UserBook, BookInstruction.book_id == UserBook.book_id
            ).filter(UserBook.user_id == user_id).all()
            return [Instruction.serialize(instruction) for instruction in instructions]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(
                f"InstructionRepo - get_user_instructions error: {e}")

    @staticmethod
    def query_book_instructions(book_id):
        """Query all instructions associated with a book"""
        try:
            book = Book.query.get(book_id)
            instructions = book.instructions
            return [Instruction.serialize(instruction) for instruction in instructions]
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(
                f"InstructionRepo - query_book_instructions error: {e}")


###################### ASSOCIATION TABLES ############################


class RecipeIngredientRepo():
    """Facilitates association of recipes & ingredients"""
    @staticmethod
    def create_ingredient(recipe_id, item_id, quantity_unit_id, quantity_amount_id):
        """Create recipe and ingredient(amount, unit, item) association -> add to database"""
        entry = Ingredient(
            recipe_id=recipe_id, item_id=item_id, quantity_unit_id=quantity_unit_id, quantity_amount_id=quantity_amount_id)
        try:
            db.session.add(entry)
            db.session.flush()
            return entry.id
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(
                f"RecipeIngredientRepo - create_ingredient error:{e}")


class RecipeBookRepo():
    """Facilitates association of recipes & books"""
    @staticmethod
    def create_entry(book_id, recipe_id):
        """Create recipe and book association -> add to database"""
        try:
            entry = RecipeBook(book_id=book_id, recipe_id=recipe_id)
            db.session.add(entry)
        except SQLAlchemyError as e:
            raise Exception(f"RecipeBookRep - create_entry error:{e}")


class UserBookRepo():
    """Facilitates association of users & books"""
    @staticmethod
    def create_entry(user_id, book_id):
        """Create user and book association -> add to database"""
        try:
            entry = UserBook(user_id=user_id, book_id=book_id)
            db.session.add(entry)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"UserBookRepo - create_entry error:{e}")


class BookInstructionRepo():
    """Facilitates association of books & instructions"""
    @staticmethod
    def create_entry(book_id, instruction_id):
        """Create book and instruction association -> add to database"""
        try:
            entry = BookInstruction(
                book_id=book_id, instruction_id=instruction_id)
            db.session.add(entry)
        except SQLAlchemyError as e:
            highlight(e, "!")
            db.session.rollback()
            raise Exception(f"BookInstructionRepo - create_entry error :{e}")


class RecipeInstructionRepo():
    """Facilitates association of recipes & instructions"""
    @staticmethod
    def create_entry(recipe_id, instruction_id):
        """Create recipe and instruction association -> add to database"""
        try:
            entry = RecipeInstruction(
                recipe_id=recipe_id, instruction_id=instruction_id)
            db.session.add(entry)
            db.session.flush()
            return entry.id
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"RecipeInstructionRepo - create_entry error :{e}")


class AmountBookRepo():
    """Facilitates association of amounts & books"""
    @staticmethod
    def create_entry(amount_id, book_id):
        """Create amount and book association -> add to database"""
        try:
            entry = AmountBook(amount_id=amount_id, book_id=book_id)
            db.session.add(entry)
            db.session.flush()
            return entry.id
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"AmountBookRepo - create_entry error :{e}")


class UnitBookRepo():
    """Facilitates association of units & books"""
    @staticmethod
    def create_entry(unit_id, book_id):
        """Create unit and book association -> add to database"""
        try:
            entry = UnitBook(unit_id=unit_id, book_id=book_id)
            db.session.add(entry)
            db.session.flush()
            return entry.id
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"UnitBookRepo - create_entry error:{e}")


class ItemBookRepo():
    """Facilitates association of items & books"""
    @staticmethod
    def create_entry(item_id, book_id):
        """Create item and book association -> add to database"""
        try:
            entry = ItemBook(item_id=item_id, book_id=book_id)
            db.session.add(entry)
            db.session.flush()
            return entry.id
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise RuntimeError(f"ItemBookRepo - create_entry error:{e}")
