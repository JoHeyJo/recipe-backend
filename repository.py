from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import User, db, Recipe, QuantityUnit, QuantityAmount, Item, Book, Instruction, Ingredient, RecipeBook, UserBook, BookInstruction, RecipeInstruction, AmountBook, UnitBook, ItemBook, BookRole, BookType
from exceptions import *
from utils.functions import insert_first, highlight
from werkzeug.exceptions import Conflict

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
                password=hashed_pwd
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
        try:
            user = User.query.filter_by(user_name=user_name).first()
            # If user exists AND user is authorized
            if user and bcrypt.check_password_hash(user.password, password):
                return create_access_token(identity=user.id)
            return False
        except Exception as e:
            raise type(e)(f"UserRepo -> login error:{e}") from e

    @staticmethod
    def _base_query():
        return db.select(User)

    @staticmethod
    def query_user(user_pk):
        """Query user by PK. Returns User or None if not found"""
        try:
            return db.session.get(User, user_pk)
        except Exception as e:
            raise type(e)(f"UserRepo -> query_user error:{e}") from e

    @staticmethod
    def query_user_name(user_name):
        """Query user by username. Returns User or None if not found."""
        try:
            stmt = UserRepo._base_query().where(User.user_name == user_name)
            return db.session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            raise type(e)(f"UserRepo -> query_user_name error:{e}") from e

    @staticmethod
    def hash_password(string):
        """Hashes string sequence"""
        return bcrypt.generate_password_hash(string).decode('UTF-8')


class RecipeRepo():
    """Facilitates recipes table interactions"""

    @staticmethod
    def query_recipe(recipe_pk):
        """Query recipe by PK. Return Recipe or None if not found"""
        try:
            return db.session.get(Recipe, recipe_pk)
        except Exception as e:
            raise type(e)(f"RecipeRepo -> create_recipe error:{e}") from e

    @staticmethod
    def create_recipe(name, notes, user_id):
        """Creates recipe instance and adds it to database"""
        recipe = Recipe(name=name, notes=notes, created_by_id=user_id)
        try:
            db.session.add(recipe)
            db.session.flush()
            return Recipe.serialize(recipe)
        except Exception as e:
            raise type(e)(f"RecipeRepo -> create_recipe error:{e}") from e

    @staticmethod
    def create_recipe_lik(recipient, shared_id):
        """Creates recipe association between User's and Recipient. All shared
        recipes will populate in recipient's "Shared Recipes" book. If book does
        not exist one will be created automatically"""
        shared_link = UserBookRepo.query_shared_book(recipient_id=recipient.id)
        book = None
        has_default_book = recipient.default_book_id
        if not shared_link:
            book = BookRepo.create_book(title="Shared Recipes",
                                        description="Inbox: Recipes shared by others", book_type=BookType.shared_inbox)

            shared_link = UserBookRepo.create_entry(
                user_id=recipient.id, book_id=book["id"])
        try:
            is_shared = RecipeBook.query.filter_by(
                book_id=shared_link.book_id, recipe_id=shared_id).first()

            if is_shared:
                return {"message": "Recipe already shared with user.",
                        "error": "Conflict", "code": 409}
# this is not returning book_with_role
# create logic for when recipient's default book is shared recipes
# look at payload when not is_shared and has_default_book and has be previously shared

# look at payload when User shares with Book with Recipient  - No default book (tester)
# Current Book is undefined after default book is created - default book is a complete object
# On refresh sharing book works
# Client needed to have context updated with relevant data
# Now book needs to populate for recipient``
# This look good!


# look at payload when User shares with Book with Recipient  - Assigned default book (tester)
# This looks good

# look at payload when User shares recipe with Recipient - No default book
# THIS LOOKS GOOD

# look at payload when User shares recipe with Recipient - Default book is standard
# recipient's dropdown list is replaced with the one shared book and recipe is render
# if another book is shared an error is thrown
# If recipient has standard default book then:
# message should be shown
# dropdown should be populated
# Shared book is not retrieved if recipient already has a shared book


# look at payload when User shares recipe with Recipient - Default book is Shared Book

            highlight(("is_shared:", is_shared,
                      "has_default_book:", has_default_book), "!")
            if not is_shared and has_default_book:
                msg = RecipeBookRepo.create_entry(
                    book_id=shared_link.book_id, recipe_id=shared_id)
                highlight(book, "!")

                book_with_role = BookRepo.build_book(
                    user_id=recipient.id, book_id=book["id"])
                
                highlight((msg, book_with_role), "!")
                return {"message": "Recipe successfully shared!", "code": 200, "payload": book_with_role}

            highlight(("is_shared:", is_shared,
                      "has_default_book:", has_default_book), "!")

        except Exception as e:
            raise type(e)(f"RecipeRepo -> create_recipe_link error:{e}") from e

    @staticmethod
    def fetch_recipes(user_id, book_id):
        """Retrieve recipes corresponding to user's book"""
        try:
            book = db.session.query(Book).filter_by(id=book_id).first()
            recipes = book.recipes
            return [Recipe.serialize(recipe) for recipe in recipes]
        except Exception as e:
            raise type(e)(f"RecipeRepo -> create_recipe error:{e}") from e

    @staticmethod
    def delete_recipe(recipe_id):
        """Deletes recipe and all references in association tables"""
        try:
            db.session.execute(
                # Use direct SQLAlchemy delete - error occurs using ORM
                db.delete(Recipe).where(Recipe.id == int(recipe_id))
            )
        except Exception as e:
            raise type(e)(f"RecipeRepo -> delete_recipe error:{e}") from e


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
            raise type(e)(
                f"QuantityAmountRepo - create_amount error:{e}") from e

    @staticmethod
    def query_all_amounts():
        """Return all amounts"""
        try:
            amounts = QuantityAmount.query.all()
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except Exception as e:
            raise type(e)(
                f"QuantityAmountRepo -  get_all_amounts error: {e}") from e

    @staticmethod
    def query_book_amounts(book_id):
        """Return user amounts"""
        try:
            amounts = db.session.query(Book).filter_by(
                id=book_id).first().amounts
            return [QuantityAmount.serialize(amount) for amount in amounts]
        except Exception as e:
            raise type(e)(
                f"QuantityAmountRepo -  get_book_amounts error: {e}") from e

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
            raise type(e)(
                f"QuantityAmountRepo - get_user_amounts error: {e}") from e


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
            raise type(e)(
                f"QuantityUnitRepo - get_all_units error: {e}") from e

    @staticmethod
    def query_book_units(book_id):
        """Return book's units"""
        try:
            units = db.session.query(Book).filter_by(
                id=book_id).first().units
            return [QuantityUnit.serialize(unit) for unit in units]
        except Exception as e:
            raise type(e)(
                f"QuantityUnitRepo - get_book_units error: {e}") from e


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
    def create_book(title, description, book_type=BookType.standard):
        """Create book and add to database"""
        try:
            book = Book(title=title, description=description,
                        book_type=book_type)
            db.session.add(book)
            db.session.flush()
            return Book.serialize(book)
        except Exception as e:
            raise type(e)(f"create_book error: {e}") from e

    @staticmethod
    def query_user_book_by_pk(book_pk):
        """Query book by pk. Return none if not found"""
        try:
            stmt = db.select(Book).where(Book.id == book_pk)
            return db.session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            raise type(e)(
                f"BookRepo - query_user_book_by_pk error: {e}") from e

    @staticmethod
    def query_user_books(user_id):
        """Returns all books associated to user"""
        try:
            user = db.session.query(User).filter_by(id=user_id).first()
            return [
                {
                    **Book.serialize(user_book.book),
                    "book_role": user_book.role.value
                }
                for user_book in user.user_books
            ]
        except Exception as e:
            raise type(e)(f"BookRepo - get_user_books error: {e}") from e

    @staticmethod
    def build_book(user_id, book_id):
        """Build book object to include 'book_role'"""
        try:
            stmt = db.select(UserBook).where(
                UserBook.book_id == book_id, UserBook.user_id == user_id)
            user_book = db.session.execute(stmt).scalar_one_or_none()
            serialized = Book.serialize(user_book.book)
            serialized["book_role"] = user_book.role.value
            return serialized
        except Exception as e:
            raise type(e)(f"BookRepo - build_book error: {e}") from e


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
            raise type(e)(
                f"InstructionRepo - create_instruction error: {e}") from e

    @staticmethod
    def get_instructions():
        """Return all instructions"""
        try:
            instructions = Instruction.query.all()
            return [Instruction.serialize(instruction) for instruction in instructions]
        except Exception as e:
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
            return entry
        except Exception as e:
            raise type(e)(f"RecipeBookRep - create_entry error:{e}") from e

    @staticmethod
    def remove_book_association(book_id, recipe_id):
        """Delete association sharing recipe to recipient"""
        try:
            recipe_book = db.session.get(
                RecipeBook, {"book_id": book_id, "recipe_id": recipe_id})
            db.session.delete(recipe_book)
            return {"message": "Recipe is no longer shared"}
        except Exception as e:
            raise type(e)(
                f"RecipeBookRep - remove_book_association error:{e}") from e

    @staticmethod
    def does_recipe_exist_in_shared_inbox(shared_link_id, shared_recipe_id):
        """Query recipe in shared_inbox return value or none"""
        try:
            stmt = db.select(RecipeBook).where(
                RecipeBook.book_id == shared_link_id, 
                RecipeBook.recipe_id == shared_recipe_id)
            
            return db.session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            raise type(e)(
                f"RecipeBookRep - does_recipe_exist_in_shared_inbox error:{e}") from e


class UserBookRepo():
    """Facilitates association of users & books"""
    @staticmethod
    def create_entry(user_id, book_id, role=BookRole.owner):
        """Create user and book association -> add to database"""
        try:
            entry = UserBook(user_id=user_id, book_id=book_id,
                             role=role)
            db.session.add(entry)
            db.session.flush()
            return entry
        except Exception as e:
            raise type(e)(f"UserBookRepo - create_entry error:{e}") from e

    @staticmethod
    def query_user_book(book_id, user_id):
        """Query UserBook by user id and book id. Return user_book or none"""
        try:
            stmt = db.select(UserBook).filter_by(
                book_id=book_id, user_id=user_id)
            return db.session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            raise type(e)(f"RecipeBookRep - query_user_book error:{e}") from e

    @staticmethod
    def query_shared_book(recipient_id):
        """Query for User's "shared recipes" book"""
        try:
            user_book = UserBook.query.join(Book).filter(
                UserBook.user_id == recipient_id, Book.book_type == BookType.shared_inbox).first()
            return user_book
        except Exception as e:
            raise type(e)(f"UserBookRepo - query_shared_book error:{e}") from e


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
            raise type(e)(
                f"BookInstructionRepo - create_entry error :{e}") from e


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
            raise type(e)(
                f"RecipeInstructionRepo - create_entry error :{e}") from e


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
