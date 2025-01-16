from sqlalchemy.exc import IntegrityError
from repository import InstructionRepo

class InstructionService():
  """Handles instructions view business logic """
  @staticmethod
  def fetch_user_instructions(user_id):
    """Retrieves user instructions"""

    try:
       instructions = InstructionRepo.query_user_instructions(user_id)
       return instructions
    except IntegrityError as e:
        raise {"error": f"Error in OptionService -> get_options: {e}"}
