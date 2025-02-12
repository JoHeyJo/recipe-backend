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
                return ItemRepo.query_all_items()
        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> get_ingredients: {e}"}

    @staticmethod
    def fetch_book_ingredient_components(book_id):
        """Retrieves book's individual ingredient components"""
        try:
            amounts = QuantityAmountRepo.get_book_amounts(book_id=book_id)
            units = QuantityUnitRepo.get_book_units(book_id=book_id)
            items = ItemRepo.get_book_items(book_id=book_id)
            return {"amounts": amounts, "units":units, "items":items}
        except IntegrityError as e:
            raise {
                "error": f"Error in IngredientService -> fetch_book_ingredients: {e}"}

    @staticmethod
    def fetch_user_ingredients(user_id):
        """Retrieves user's individual ingredient components"""
        try:
            amounts = QuantityAmountRepo.query_user_amounts(user_id=user_id)
            units = QuantityUnitRepo.query_user_units(user_id=user_id)
            items = ItemRepo.query_user_items(user_id=user_id)
            return {"amounts": amounts, "units": units, "items": items}
        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> get_user_options: {e}"}

    @staticmethod
    def post_ingredient(component, option, book_id):
        """Calls corresponding ingredient component method for processing"""
        try:
            if component == "amount":
                return QuantityAmountRepo.process_amount(amount=option, book_id=book_id)
            if component == "unit":
                return QuantityUnitRepo.process_unit(unit=option, book_id=book_id)
            if component == "item":
                return ItemRepo.process_item(item=option, book_id=book_id)
        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> add_ingredient: {e}"}

    # @staticmethod
    # def create_option_association(book_id, option_id)