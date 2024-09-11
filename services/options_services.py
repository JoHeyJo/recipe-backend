from repository import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

class OptionService():
    """Handles option view business logic"""
    @staticmethod
    def get_options(option):
        """Retrieves options for ingredient components"""
        try:
            if option == "amounts":
                  return QuantityAmountRepo.get_all_amounts()
            if option == "units":
                  return QuantityUnitRepo.get_all_units()
            if option == "items":
                  return IngredientRepo.get_all_ingredients()
        except IntegrityError as e:
            raise {"error": f"Error in OptionService -> get_options: {e}"}
        
    @staticmethod
    def add_option(option, value):
        """Add option to specified ingredient component"""
        try:
           if option == "amount":
               return QuantityAmountRepo.process_amount(amount=value)
           if option == "unit":
               return QuantityUnitRepo.process_unit(unit=value)
           if option == "ingredient":
               return IngredientRepo.process_ingredient(ingredient=value)
        except IntegrityError as e:
             raise {"error": f"Error in OptionService -> get_options: {e}"}