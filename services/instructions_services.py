from sqlalchemy.exc import IntegrityError
from repository import InstructionRepo
from models import db, User
from repository import highlight, UserBook, BookInstructionRepo

class InstructionService():
  """Handles instructions view business logic """

  @staticmethod
  def fetch_user_instructions(user_id):
    """Retrieves user instructions"""
    try:
       instructions = InstructionRepo.query_user_instructions(user_id)
       return instructions
    except IntegrityError as e:
        raise {"error": f"Error in InstructionService -> fetch_user_instructions: {e}"}

  @staticmethod
  def fetch_book_instructions(book_id):
     """Retrieves book instructions"""
     try:
        instructions = InstructionRepo.query_book_instructions(book_id)
        return instructions
     except IntegrityError as e:
         raise {"error": f"Error in InstructionService -> fetch_book_instructions: {e}"}
     
  @staticmethod
  def check_book_access(user_id, book_id):
     """Authorizes user access to book"""
     try:
        book_ids = [book_id[0] for book_id in db.session.query(
            UserBook.book_id).filter(UserBook.user_id == user_id).all()]
        if int(book_id) in book_ids:
           return True
        else:
           return False
     except IntegrityError as e:
         raise {"error": f"Error in InstructionService -> check_user_access: {e}"}
     
  @staticmethod
  def post_instruction_association(book_id, instruction_id):
     """Add instruction to association table"""
     try:
        BookInstructionRepo.create_entry(book_id=book_id, instruction_id=instruction_id)
     except IntegrityError as e:
         raise {
             "error": f"Error in InstructionService -> post_instruction_association: {e}"}
