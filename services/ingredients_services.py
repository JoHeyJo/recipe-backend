from repository import *


class IngredientServices():
    """Handles ingredients view business logic"""
    @staticmethod
    # NOT IN USE
    def fetch_components_options(ingredient):
        """Retrieves individual ingredient components"""
        try:
            if ingredient == "amounts":
                return QuantityAmountRepo.query_all_amounts()
            if ingredient == "units":
                return QuantityUnitRepo.query_all_units() #needs to be created
            if ingredient == "items":
                return ItemRepo.query_all_items()
        except Exception as e:
            raise type(e)(
                f"Error in IngredientServices -> fetch_components_options: {e}") from e

    @staticmethod
    def fetch_book_components_options(book_id):
        """Retrieves book's ingredients components options"""
        try:
            amounts = QuantityAmountRepo.query_book_amounts(book_id=book_id)
            units = QuantityUnitRepo.query_book_units(book_id=book_id)
            items = ItemRepo.query_book_items(book_id=book_id)
            return {"amounts": amounts, "units": units, "items": items}
        except Exception as e:
            raise type(e)(
                f"Error in IngredientServices -> fetch_book_components_options: {e}") from e

    @staticmethod
    def fetch_user_components_options(user_id):
        """Retrieves user's individual ingredient components"""
        try:
            amounts = QuantityAmountRepo.query_user_amounts(user_id=user_id)
            units = QuantityUnitRepo.query_user_units(user_id=user_id)
            items = ItemRepo.query_user_items(user_id=user_id)
            return {"amounts": amounts, "units": units, "items": items}
        except Exception as e:
            raise type(e)(
                f"Error in IngredientServices -> fetch_user_components_options: {e}") from e

    @staticmethod
    def post_component_option(component, option, book_id):
        """Calls corresponding ingredient component method for processing.
        Session is in autocommit mode - using SQLAlchemy core for insert"""
        try:
            if component == "amount":
                return AmountServices.process_amount(amount=option, book_id=book_id)
            if component == "unit":
                return UnitServices.process_unit(unit=option, book_id=book_id)
            if component == "item":
                item =  ItemServices.process_item(item=option, book_id=book_id)
                db.session.commit()
                return item
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"Error in IngredientServices -> post_component_option: {e}") from e

    @staticmethod
    def create_option_association(component, book_id, option_id):
        """Associate user option to book"""
        try:
            if component == "amount":
                AmountBookRepo.create_entry(
                    amount_id=option_id, book_id=book_id)
            if component == "unit":
                UnitBookRepo.create_entry(unit_id=option_id, book_id=book_id)
            if component == "item":
                ItemBookRepo.create_entry(item_id=option_id, book_id=book_id)
            db.session.commit()
            return {"message": f"Successful association of option {option_id} to book {book_id}!"}
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"IngredientServices -> create_option_association error: {e}") from e

    @staticmethod
    def process_ingredient_components(book_id, ingredients):
        """Separates & processes ingredient components - creates ingredient return object"""
        ingredients_data = []
        for ingredient in ingredients:
            item = ingredient["item"]
            amount = ingredient["amount"]
            unit = ingredient["unit"]

            if not item and not amount and not unit:
                raise ValueError("Nothing to process in ingredients")
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

            except Exception as e:
                raise type(e)(
                    f"IngredientsRepo -> process_ingredients error: {e}") from e
        return ingredients_data

    @staticmethod
    def build_ingredients(instance):
        """Build ingredient from corresponding instances(Recipe)"""
        ingredients = []
        try:
            for ingredient in instance.ingredients:
                amount = QuantityAmount.serialize(ingredient.amount)
                unit = QuantityUnit.serialize(ingredient.unit)
                item = Item.serialize(ingredient.item)
                ingredients.append(
                    {"ingredient_id": ingredient.id, "amount": amount, "unit": unit, "item": item})
            return ingredients
        except Exception as e:
            raise type(e)(
                f"Ingredient_services - build_ingredients error, missing value: {e}") from e


class ItemServices():
    """Handles ingredient's component ITEM services"""
    @staticmethod
    def process_item(item, book_id):
        """Create and returns new item or return existing item - Associates item to book"""
        try:
            is_stored = item.get("id")
            if is_stored is None:
                item = ItemRepo.create_item(name=item["name"])
            ItemBookRepo.create_entry(item_id=item["id"], book_id=book_id)
            return item
        except Exception:
            raise


class AmountServices():
    """Handles ingredient's component AMOUNT services"""
    @staticmethod
    def process_amount(amount, book_id):
        """Creates and returns new amount or return existing amount - Associates amount to book """
        try:
            is_stored = amount.get("id")
            if is_stored is None:
                amount = QuantityAmountRepo.create_amount(
                    value=amount["value"])
            AmountBookRepo.create_entry(
                amount_id=amount["id"], book_id=book_id)
            return amount
        except Exception:
            raise


class UnitServices():
    """Handles ingredient's component UNIT services"""
    @staticmethod
    def process_unit(unit, book_id):
        """Creates and returns new unit or returns existing unit - Associates unit to book"""
        try:
            is_stored = unit.get("id")
            if is_stored is None:
                unit = QuantityUnitRepo.create_unit(type=unit["type"])
            UnitBookRepo.create_entry(unit_id=unit["id"], book_id=book_id)
            return unit
        except Exception:
            raise
