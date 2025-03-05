from repository import *
from sqlalchemy.exc import IntegrityError
from utils.error_handler import handle_exception


class IngredientServices():
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
                "error": f"Error in IngredientServices -> fetch_components_options: {e}"}

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
                "error": f"Error in IngredientServices -> fetch_book_components_options: {e}"}

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
                "error": f"Error in IngredientServices -> fetch_user_components_options: {e}"}

    @staticmethod
    def post_component_option(component, option, book_id):
        """Calls corresponding ingredient component method for processing"""
        try:
            if component == "amount":
                return QuantityAmountRepo.process_amount(amount=option, book_id=book_id)
            if component == "unit":
                return QuantityUnitRepo.process_unit(unit=option, book_id=book_id)
            if component == "item":
                return ItemServices.process_item(item=option, book_id=book_id)
        except IntegrityError as e:
            raise {"error": f"Error in IngredientServices -> post_component_option: {e}"}

    @staticmethod
    def create_option_association(component, book_id, option_id):
        """Associate user option to book"""
        try:
            if component == "amount":
                AmountBookRepo.create_entry(amount_id=option_id, book_id=book_id)
            if component == "unit":
                UnitBookRepo.create_entry(unit_id=option_id, book_id=book_id)
            if component == "item":
                ItemBookRepo.create_entry(item_id=option_id, book_id=book_id)
        except IntegrityError as e:
            raise Exception(f"IngredientServices -> create_option_association error: {e}")
    
    @staticmethod
    def process_ingredient_components(book_id, ingredients):
        """Separates & processes ingredient components - creates ingredient return object"""
        ingredients_data = []
        for ingredient in ingredients:
            item = ingredient["item"]
            amount = ingredient["amount"]
            unit = ingredient["unit"]

            if not item and not amount and not unit:
                return {"message":"Nothing to process"}
            try:
                item = ItemServices.process_item(item=item, book_id=book_id)
                if amount:
                    amount = AmountServices.process_amount(
                        amount=amount, book_id=book_id)
                if unit:
                    unit = UnitServices.process_unit(
                        unit=unit, book_id=book_id)

                ingredients_data.append(
                    {
                        "item": item,
                        "amount": amount,
                        "unit": unit
                    })

            except SQLAlchemyError as e:
                highlight(e, "!")
                raise Exception(
                    f"IngredientsRepo -> process_ingredients error: {e}")
        return ingredients_data


class ItemServices():
    """Handles ingredient's component ITEM services"""
    @staticmethod
    def process_item(item, book_id):
        """Create and returns new item or return existing item - Associates item to book"""
        is_stored = item.get("id")
        try:
            if is_stored is None:
                item = ItemRepo.create_item(name=item["name"])
            ItemBookRepo.create_entry(item_id=item["id"], book_id=book_id)
            return item
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"ItemServices - process_item error: {e}")

class AmountServices():
    """Handles ingredient's component AMOUNT services"""
    @staticmethod
    def process_amount(amount, book_id):
        """Creates and returns new amount or return existing amount - Associates amount to book """
        is_stored = amount.get("id")
        try:
            if is_stored is None:
                amount = QuantityAmountRepo.create_amount(
                    value=amount["value"])
            AmountBookRepo.create_entry(
                amount_id=amount["id"], book_id=book_id)
            return amount
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"AmountServices - process_amount error, {e}")

class UnitServices():
    """Handles ingredient's component UNIT services"""
    @staticmethod
    def process_unit(unit, book_id):
        """Creates and returns new unit or returns existing unit - Associates unit to book"""
        is_stored = unit.get("id")
        try:
            if is_stored is None:
                unit = QuantityUnitRepo.create_unit(type=unit["type"])
            UnitBookRepo.create_entry(unit_id=unit["id"], book_id=book_id)
            return unit
        except SQLAlchemyError as e:
            highlight(e, "!")
            raise Exception(f"UnitServices - process_unit error, {e}")
