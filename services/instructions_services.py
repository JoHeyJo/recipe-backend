from sqlalchemy.exc import IntegrityError, SQLAlchemyError, ProgrammingError
from repository import InstructionRepo
from models import db, Instruction
from repository import UserBookRepo, BookInstructionRepo, RecipeInstructionRepo
from werkzeug.exceptions import Conflict
from utils.functions import highlight

class InstructionServices():
    """Handles instructions view business logic"""
    @staticmethod
    def fetch_user_instructions(user_id):
        """Retrieves user instructions"""
        try:
            instructions = InstructionRepo.query_user_instructions(user_id)
            return instructions
        except IntegrityError as e:
            raise (
                f"Error in InstructionServices -> fetch_user_instructions: {e}") from e

    @staticmethod
    def fetch_book_instructions(book_id, user_id):
        """Retrieves book instructions"""
        has_access = InstructionServices.check_book_access(
            user_id=user_id, book_id=book_id)
        if has_access:
            try:
                instructions = InstructionRepo.query_book_instructions(book_id)
                return instructions
            except Exception as e:
                raise type(e)(
                    f"Error in InstructionServices -> fetch_book_instructions: {e}") from e
        else:
            raise ProgrammingError("User does not have access to book")

    @staticmethod
    def check_book_access(user_id, book_id):
        """Authorizes user access to book"""
        try:
            book_ids = UserBookRepo.query_user_book_ids(
                user_id=user_id, book_id=book_id)
            if int(book_id) in book_ids:
                return True
            else:
                return False
        except Exception as e:
            raise type(e)(
                f"Error in InstructionServices -> check_user_access: {e}") from e

    @staticmethod
    def process_book_instruction(request, book_id):
        """Create instruction and association to corresponding book"""
        try:
            instruction = request["instruction"]
            created_instruction = InstructionRepo.create_instruction(
                instruction=instruction)
            InstructionServices.create_instruction_association(
                book_id=book_id, instruction_id=created_instruction["id"])
            db.session.commit()
            return created_instruction
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"Error in InstructionServices - process_book_instruction") from e

    @staticmethod
    def create_instruction_association(book_id, instruction_id):
        """Associate user instruction to book"""
        try:
            # prevents User from creating duplicate association to book
            exists = BookInstructionRepo.query_book_instruction(
                book_id=book_id, instruction_id=instruction_id)
            if exists:
                return
            
            BookInstructionRepo.create_entry(
                book_id=book_id, instruction_id=instruction_id)
            db.session.commit()
            return {"message":
                    f"Successful association of instruction {instruction_id} to book {book_id}!"}
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"Error in InstructionServices -> create_instruction_association: {e}") from e

    @staticmethod
    def process_instructions(instructions, recipe_id):
        """Associates instructions to recipe """
        for instruction in instructions:
            try:
                RecipeInstructionRepo.create_entry(recipe_id=recipe_id, instruction_id=instruction["id"])
            except Exception as e:
                db.session.rollback()
                raise type(e)(
                    f"Error in InstructionServices - process_instructions: {e}") from e
        return instructions

    @staticmethod
    def build_instructions(instances):
        """Return serialized instructions instructions instance"""
        if not instances:
            return []
        try:
            return [Instruction.serialize(instruction_instance) for instruction_instance in instances]
        except Exception as e:
            raise type(e)(
                f"InstructionServices - build_instructions error: {e}") from e
