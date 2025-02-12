from repository import *
from sqlalchemy.exc import IntegrityError


class IngredientService():
    """Handles ingredients view business logic"""
    @staticmethod
    def fetch_components_options(ingredient):
        """Retrieves individual ingredient components"""
        try:
            if ingredient == "amounts":
                return QuantityAmountRepo.get_all_amounts()
            if ingredient == "units":
                return QuantityUnitRepo.get_all_units()
            if ingredient == "items":
                return ItemRepo.query_all_items()
        except IntegrityError as e:
            raise {
                "error": f"Error in IngredientService -> fetch_components_options: {e}"}

    @staticmethod
    def fetch_book_components_options(book_id):
        """Retrieves book's ingredients components options"""
        try:
            amounts = QuantityAmountRepo.get_book_amounts(book_id=book_id)
            units = QuantityUnitRepo.get_book_units(book_id=book_id)
            items = ItemRepo.get_book_items(book_id=book_id)
            return {"amounts": amounts, "units":units, "items":items}
        except IntegrityError as e:
            raise {
                "error": f"Error in IngredientService -> fetch_book_components_options: {e}"}

    @staticmethod
    def fetch_user_components_options(user_id):
        """Retrieves user's individual ingredient components"""
        try:
            amounts = QuantityAmountRepo.query_user_amounts(user_id=user_id)
            units = QuantityUnitRepo.query_user_units(user_id=user_id)
            items = ItemRepo.query_user_items(user_id=user_id)
            return {"amounts": amounts, "units": units, "items": items}
        except IntegrityError as e:
            raise {
                "error": f"Error in IngredientService -> fetch_user_components_options: {e}"}

    @staticmethod
    def post_component_option(component, option, book_id):
        """Calls corresponding ingredient component method for processing"""
        try:
            if component == "amount":
                return QuantityAmountRepo.process_amount(amount=option, book_id=book_id)
            if component == "unit":
                return QuantityUnitRepo.process_unit(unit=option, book_id=book_id)
            if component == "item":
                return ItemRepo.process_item(item=option, book_id=book_id)
        except IntegrityError as e:
            raise {"error": f"Error in IngredientService -> post_component_option: {e}"}

    @staticmethod
    def create_option_association(component, book_id, option_id):
        """Associate user option to book"""
        try:
            if component == "amount":
                
            if component == "unit":
            if component == "item":