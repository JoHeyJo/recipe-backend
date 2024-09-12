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
                  return ItemRepo.get_all_items()
        except IntegrityError as e:
            raise {"error": f"Error in OptionService -> get_options: {e}"}
        
    @staticmethod
    def add_option(label, attributes):
        """Call corresponding ingredient component method for processing"""
        try:
           if label == "value":
               return QuantityAmountRepo.process_amount(amount=attributes)
           if label == "type":
               return QuantityUnitRepo.process_unit(unit=attributes)
           if label == "name":
               return ItemRepo.process_item(item=attributes)
        except IntegrityError as e:
             raise {"error": f"Error in OptionService -> get_options: {e}"}