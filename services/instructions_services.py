from sqlalchemy.exc import IntegrityError
from repository import InstructionRepo
from models import User
from repository import highlight

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
  def check_user_access(user_id, book_id):
     """Verifies/denies user access to book"""
     try:
        user_books = User.query.get(user_id).books
        highlight(user_books,"@")
        if book_id in user_books:
           return True
        else:
           return False
     except IntegrityError as e:
         raise {"error": f"Error in InstructionService -> check_user_access: {e}"}
