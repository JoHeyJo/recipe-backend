from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from repository import InstructionRepo
from models import db, User
from repository import highlight, UserBook, BookInstructionRepo


class InstructionServices():
    """Handles instructions view business logic """
    @staticmethod
    def fetch_user_instructions(user_id):
      """Retrieves user instructions"""
      try:
         instructions = InstructionRepo.query_user_instructions(user_id)
         return instructions
      except IntegrityError as e:
          raise (f"Error in InstructionServices -> fetch_user_instructions: {e}")
    
    @staticmethod
    def fetch_book_instructions(book_id):
       """Retrieves book instructions"""
       try:
          instructions = InstructionRepo.query_book_instructions(book_id)
          return instructions
       except IntegrityError as e:
           raise (
               f"Error in InstructionServices -> fetch_book_instructions: {e}")
    
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
           raise (f"Error in InstructionServices -> check_user_access: {e}")
    
    @staticmethod
    def create_instruction_association(book_id, instruction_id):
       """Associate user instruction to book"""
       try:
          BookInstructionRepo.create_entry(
              book_id=book_id, instruction_id=instruction_id)
       except IntegrityError as e:
           raise (
               f"Error in InstructionServices -> create_instruction_association: {e}")
    
    @staticmethod
    def process_instructions(instructions, book_id):
          """Adds new instructions - Consolidates existing and new instruction objects - associates instruction to book """
          processed_instructions = []
          for instruction in instructions:
              is_stored = instruction.get("id")
              if is_stored is None:
                  try:
                      instruction = InstructionRepo.create_instruction(
                          instruction=instruction["instruction"])
                      processed_instructions.append(instruction)
                      BookInstructionRepo.create_entry(
                          book_id=book_id, instruction_id=instruction.id)
                  except SQLAlchemyError as e:
                      raise Exception(f"InstructionRepo - process_instructions error: {e}")
              else:
                  processed_instructions.append(instruction)
          return processed_instructions