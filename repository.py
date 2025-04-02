from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import User, db, Recipe, QuantityUnit, QuantityAmount, Item, Book, Instruction, Ingredient, RecipeBook, UserBook, BookInstruction, RecipeInstruction, AmountBook, UnitBook, ItemBook
from exceptions import *
from utils.functions import insert_first

bcrypt = Bcrypt()

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
        except Exception as e:
            # can be moved to handle_route_errors
            if "users_user_name_key" in str(e.orig):
                raise UsernameAlreadyTakenError(
                    "This username is already taken.") from e
            elif "users_email_key" in str(e.orig):
                raise EmailAlreadyRegisteredError(
                    "This email is already taken.") from e
            else:
                raise SignUpError("An error occurred during signup.") from e

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
            user = db.session.query(User).filter_by(id=user_id).first()
            if user is None:
                return None 
            return user
        except Exception as e:
            raise type(e)(f"UserRepo -> query_user error:{e}")


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
        except Exception as e:
            raise type(e)(f"create_recipe error:{e}") from e

    @staticmethod
    def fetch_recipes(user_id, book_id):
        """Retrieve recipes corresponding to user's book"""
        try:
            book = db.session.query(Book).filter_by(id=book_id).first()
            recipes = book.recipes
            return [Recipe.serialize(recipe) for recipe in recipes]
        except Exception as e:
            raise type(e)(f"create_recipe error:{e}")

    @staticmethod
    def delete_recipe(recipe_id):
        """Deletes recipe and all references in association tables"""
        try:
            db.session.execute(
                # Use direct SQLAlchemy delete - error occurs using ORM
                db.delete(Recipe).where(Recipe.id == int(recipe_id))
            )
        except Exception as e:
            raise type(e)(f"delete_recipe error:{e}") from e


class QuantityAmountRepo():
    """Process amounts & facilitates quantity_amounts table interactions"""
    @staticmethod
    def create_amount(value):
        """Create quantity amount and add to database."""
        try:
            quantity_amount = insert_first(
                Model=QuantityAmount, data=value, column_name="value", db=db)
            return QuantityAmount.serialize(quantity_amount)
        except Exception as e:
            raise type(e)(f"QuantityAmountRepo - create_amount error:{e}") from e

    @staticmethod
    def query_all_amounts():
        """Return all amounts"""
        try:
            amounts = QuantityAmount.query.all()
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except Exception as e:
            # db.session.rollback()
            raise type(e)(f"QuantityAmountRepo -  get_all_amounts error: {e}") from e

    @staticmethod
    def query_book_amounts(book_id):
        """Return user amounts"""
        try:
            amounts = db.session.query(Book).filter_by(id=book_id).first().amounts
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except Exception as e:
            raise type(e)(f"QuantityAmountRepo -  get_book_amounts error: {e}") from e

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
        except Exception as e:
            raise type(e)(f"QuantityAmountRepo - get_user_amounts error: {e}") from e


class QuantityUnitRepo():
    """Facilitates quantity_units table interactions"""
    @staticmethod
    def create_unit(type):
        """Create quantity unit and add to database"""
        try:
            quantity_unit = insert_first(
                Model=QuantityUnit, data=type, column_name="type", db=db)
            return QuantityUnit.serialize(quantity_unit)
        except Exception as e:
            raise type(e)(f"QuantityUnitRepo - create_unit:{e}") from e

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
        except Exception as e:
            raise type(e)(f"QuantityUnitRepo - get_all_units error: {e}") from e

    @staticmethod
    def query_book_units(book_id):
        """Return book's units"""
        try:
            units = db.session.query(Book).filter_by(
                id=book_id).first().units
            return [QuantityUnit.serialize(unit) for unit in units]
        except Exception as e:
            raise type(e)(f"QuantityUnitRepo - get_book_units error: {e}") from e


class ItemRepo():
    """Processes item & facilitates table interactions"""
    @staticmethod
    def create_item(name):
        """Create item and add to database"""
        try:
            item = insert_first(
                Model=Item, data=name, column_name="name", db=db)
            return Item.serialize(item)
        except Exception as e:
            raise type(e)(f"ItemRepo - create_item error: {e}") from e

    @staticmethod
    def query_all_items():
        """Return all items"""
        try:
            items = Item.query.all()
            return [Item.serialize(item) for item in items]
        except Exception as e:
            raise type(e)(f"get_all_item error: {e}") from e

    @staticmethod
    def query_book_items(book_id):
        """Return book's items"""
        try:
            items = db.session.query(Book).filter_by(id=book_id).first().items
            return [Item.serialize(item) for item in items]
        except Exception as e:
            raise type(e)(f"get_book_items error: {e}") from e

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
        except Exception as e:
            raise type(e)(f"query_user_items error: {e}") from e


class IngredientsRepo():
    """Directs incoming data to corresponding repo methods"""

class BookRepo():
    """Facilitates books table interactions"""
    @staticmethod
    def create_book(title, description):
        """Create book and add to database"""
        try:
            book = Book(title=title, description=description)
            db.session.add(book)
            db.session.flush()
            return Book.serialize(book)
        except Exception as e:
            raise type(e)(f"create_book error: {e}") from e

    @staticmethod
    def query_user_books(user_id):
        """Returns all books associated to user"""
        try:
            user = db.session.query(User).filter_by(id=user_id).first()
            return [Book.serialize(book) for book in user.books]
        except Exception as e:
            raise type(e)(f"BookRepo - get_user_books error: {e}") from e


class InstructionRepo():
    """Facilitates instructions table interactions"""
    @staticmethod
    def create_instruction(instruction):
        """Create and add instruction to database"""
        try:
            instruction = Instruction(instruction=instruction)
            db.session.add(instruction)
            db.session.flush()
            return Instruction.serialize(instruction)
        except Exception as e:
            raise type(e)(f"InstructionRepo - create_instruction error: {e}") from e

    @staticmethod
    def get_instructions():
        """Return all instructions"""
        try:
            instructions = Instruction.query.all()
            return [Instruction.serialize(instruction) for instruction in instructions]
        except Exception as e:
            # db.session.rollback()
            raise type(e)(f"InstructionRepo - get_instruction error: {e}")

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
        except Exception as e:
            # db.session.rollback()
            raise type(e)(
                f"InstructionRepo - get_user_instructions error: {e}")

    @staticmethod
    def query_book_instructions(book_id):
        """Query all instructions associated with a book"""
        try:
            book = db.session.query(Book).filter_by(id=book_id).first()
            instructions = book.instructions
            return [Instruction.serialize(instruction) for instruction in instructions]
        except Exception as e:
            raise type(e)(
                f"InstructionRepo - query_book_instructions error: {e}") from e


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
        except Exception as e:
            raise type(e)(
                f"RecipeIngredientRepo - create_ingredient error:{e}") from e


class RecipeBookRepo():
    """Facilitates association of recipes & books"""
    @staticmethod
    def create_entry(book_id, recipe_id):
        """Create recipe and book association -> add to database"""
        try:
            entry = RecipeBook(book_id=book_id, recipe_id=recipe_id)
            db.session.add(entry)
        except Exception as e:
            raise type(e)(f"RecipeBookRep - create_entry error:{e}") from e


class UserBookRepo():
    """Facilitates association of users & books"""
    @staticmethod
    def create_entry(user_id, book_id):
        """Create user and book association -> add to database"""
        try:
            entry = UserBook(user_id=user_id, book_id=book_id)
            db.session.add(entry)
        except Exception as e:
            raise type(e)(f"UserBookRepo - create_entry error:{e}") from e


class BookInstructionRepo():
    """Facilitates association of books & instructions"""
    @staticmethod
    def create_entry(book_id, instruction_id):
        """Create book and instruction association -> add to database"""
        try:
            entry = BookInstruction(
                book_id=book_id, instruction_id=instruction_id)
            db.session.add(entry)
        except Exception as e:
            raise type(e)(f"BookInstructionRepo - create_entry error :{e}") from e


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
        except Exception as e:
            raise type(e)(f"RecipeInstructionRepo - create_entry error :{e}") from e


class AmountBookRepo():
    """Facilitates association of amounts & books"""
    @staticmethod
    def create_entry(amount_id, book_id):
        """Create amount and book association -> add to database"""
        try:
            entry = AmountBook(amount_id=amount_id, book_id=book_id)
            db.session.add(entry)
            # db.session.flush()
            # return entry.id
        except Exception as e:
            raise type(e)(f"AmountBookRepo - create_entry error :{e}") from e


class UnitBookRepo():
    """Facilitates association of units & books"""
    @staticmethod
    def create_entry(unit_id, book_id):
        """Create unit and book association -> add to database"""
        try:
            entry = UnitBook(unit_id=unit_id, book_id=book_id)
            db.session.add(entry)
            # db.session.flush()
            # return entry.id
        except Exception as e:
            raise type(e)(f"UnitBookRepo - create_entry error:{e}") from e


class ItemBookRepo():
    """Facilitates association of items & books"""
    @staticmethod
    def create_entry(item_id, book_id):
        """Create item and book association -> add to database"""
        try:
            entry = ItemBook(item_id=item_id, book_id=book_id)
            db.session.add(entry)
            # db.session.flush()
            # return entry.id
        except Exception as e:
            raise type(e)(f"ItemBookRepo - create_entry error:{e}") from e
