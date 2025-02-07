from repository import *
from sqlalchemy.exc import IntegrityError


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

    @staticmethod
    def fetch_book_ingredients(book_id, attribute):
        """Retrieves book's individual ingredient components"""
        try:
            if attribute == "amount":
                return QuantityAmountRepo.get_book_amounts(book_id=book_id)
            if attribute == "unit":
                return QuantityUnitRepo.get_book_units(book_id=book_id)
        except IntegrityError as e:
            raise {
                "error": f"Error in IngredientService -> fetch_book_ingredients: {e}"}

    @staticmethod
    # needs to be refactored 
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
    def add_ingredient(attribute, data, book_id):
        """Calls corresponding ingredient attribute method for processing"""
        try:
            if attribute == "amount":
                return QuantityAmountRepo.process_amount(amount=data, book_id=book_id)
            if attribute == "unit":
                return QuantityUnitRepo.process_unit(unit=data, book_id=book_id)
            if attribute == "item":
                return ItemRepo.process_item(item=data, book_id=book_id)
        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> add_ingredient: {e}"}
