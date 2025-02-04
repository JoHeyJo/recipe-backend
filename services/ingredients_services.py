from repository import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class IngredientService():
    """Handles ingredients view business logic"""
    @staticmethod
    def fetch_ingredients(ingredient):
        """Retrieves individual ingredient components"""
        try:
            if ingredient == "amounts":
                return QuantityAmountRepo.get_all_amounts()
            if ingredient == "units":
                return QuantityUnitRepo.get_all_units()
            if ingredient == "items":
                return ItemRepo.get_all_items()
        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> get_ingredients: {e}"}
        # WIP: needs to be refactored to associate added ingredient to user and/or book

    @staticmethod
    def fetch_user_ingredients(user_id, ingredient):
        """Retrieves user's individual ingredient components"""
        try:
            if ingredient == "amounts":
                return QuantityAmountRepo.get_all_amounts()
            if ingredient == "units":
                return QuantityUnitRepo.get_all_units()
            if ingredient == "items":
                return ItemRepo.get_all_items()

        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> get_user_options: {e}"}

    @staticmethod
    def add_ingredient(component, option, book_id):
        """Calls corresponding ingredient component method for processing"""
        try:
            if component == "value":
                return QuantityAmountRepo.process_amount(amount=option, book_id=book_id)
            if component == "type":
                return QuantityUnitRepo.process_unit(unit=option, book_id=book_id)
            if component == "name":
                return ItemRepo.process_item(item=option, book_id=book_id)
        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> add_ingredient: {e}"}
