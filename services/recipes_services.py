from repository import *
from services.ingredients_services import IngredientServices
from services.instructions_services import InstructionServices
from sqlalchemy.exc import SQLAlchemyError
from utils.functions import highlight


class RecipeServices():
    """Handles recipe view business logic"""
    @staticmethod
    def process_recipe_data(request, book_id):
        """Consolidate 'create recipe' process"""
        try:
            recipe = request["recipe"]
            notes = recipe.get("notes")
            instructions = recipe.get("instructions")
            ingredients = recipe.get("ingredients")
        except Exception as e:
            raise type(e)(
                f"Failed to extract recipe data for book {book_id}: {e}") from e

        try:
            recipe_data = RecipeServices.process_recipe(
                book_id=book_id, recipe_name=recipe["name"], notes=notes)

            if ingredients:
                recipe_data["ingredients"] = RecipeServices.process_ingredients(
                    ingredients=ingredients, recipe_id=recipe_data["id"], book_id=book_id)
            else:
                recipe_data["ingredients"] = []

            if instructions:
                recipe_data["instructions"] = RecipeServices.process_consolidated_instructions(
                    recipe_id=recipe_data["id"], instructions=instructions, book_id=book_id)
            else:
                recipe_data["instructions"] = []

            db.session.commit()

            return recipe_data
        except Exception as e:
            db.session.rollback()
            raise type(e)(f"Failed to process_recipe_data: {e}") from e

    @staticmethod
    def process_recipe(book_id, recipe_name, notes):
        """Adds recipes and associates new recipe to book"""
        try:
            recipe_data = RecipeRepo.create_recipe(
                name=recipe_name, notes=notes)
            
            RecipeBookRepo.create_entry(
                book_id=book_id, recipe_id=recipe_data["id"])

            return recipe_data
        except Exception as e:
            raise type(e)(
                f"Failed to process recipe '{recipe_name}' for book {book_id}: {e}") from e

    @staticmethod
    def process_ingredients(ingredients, recipe_id, book_id):
        """Processes ingredient components effectively creating an ingredient and associates each ingredient to recipe"""
        try:
            ingredients_data = IngredientServices.process_ingredient_components(
                book_id=book_id, ingredients=ingredients)
            
            if not ingredients_data:
                raise ValueError(
                    f"No ingredients data returned for recipe {recipe_id}")
            
            for ingredient in ingredients_data:
                id = RecipeIngredientRepo.create_ingredient(
                    recipe_id=recipe_id,
                    item_id=ingredient["item"]['id'],
                    quantity_amount_id=ingredient["amount"]['id'],
                    quantity_unit_id=ingredient["unit"]['id'])
                ingredient["ingredient_id"] = id

            return ingredients_data
        except Exception as e:
            raise type(e)(
                f"Failed to process_ingredients for recipe {recipe_id}: {e}") from e

    @staticmethod
    def process_consolidated_instructions(recipe_id, instructions, book_id):
        """Processes consolidated instructions and associates each instruction to Recipe"""
        try:
            instructions_data = InstructionServices.process_instructions(
                instructions=instructions,book_id=book_id)

            if not instructions_data:
                raise ValueError(
                    f"No instructions data returned for book id: {book_id}") 

            for instruction in instructions_data:
                id = RecipeInstructionRepo.create_entry(
                    recipe_id=recipe_id, instruction_id=instruction["id"])
                instruction["instruction_id"] = id

            return instructions_data
        except Exception as e:
            raise type(e)(
                f"Failed to process_consolidated_instructions for book {book_id}: {e}") from e

    @staticmethod
    def build_recipes(book_id):
        """Consolidate recipe parts: recipe info, instructions, ingredients"""
        complete_recipes = []
        try:
            book = Book.query.get(book_id)
            if not book:
                raise ValueError(f"No book found with ID {book_id}")

            recipes_instances = book.recipes
            for recipe_instance in recipes_instances:
                recipe_build = {}

                recipe = Recipe.serialize(recipe_instance)
                
                recipe_build.update(recipe)

                instructions = InstructionServices.build_instructions(
                    instances=recipe_instance.instructions, recipe_id=recipe["id"])
                recipe_build["instructions"] = instructions

                ingredients = IngredientServices.build_ingredients(instance=recipe_instance)
                recipe_build["ingredients"] = ingredients

                complete_recipes.append(recipe_build)
            return complete_recipes
        except Exception as e:
            raise type(e)(f"RecipeServices - build_recipes error: {e}") from e

    @staticmethod
    def process_edit(data, recipe_id):
        """Consolidates recipe edit process"""
        try:
            name = data.get("name")
            ingredients = data.get("ingredients")
            instructions = data.get("instructions")
            notes = data.get("notes")
        except Exception as e:
            raise type(e)(
                f"Failed to extract recipe edit data for recipe {recipe_id}: {e}") from e

        try:
            if name or notes:
                RecipeServices.process_edit_recipe_info(
                    name=name, notes=notes, recipe_id=recipe_id)

            if ingredients:
                RecipeServices.process_edit_ingredients(
                    ingredients=ingredients, recipe_id=recipe_id)

            if instructions:
                RecipeServices.process_edit_instructions(
                    instructions=instructions, recipe_id=recipe_id)

            db.session.commit()
            return {"message": "edit successful"}
        except Exception as e:
            db.session.rollback()
            raise type(e)(f"Failed to process_edit: {e}") from e

    @staticmethod
    def process_edit_recipe_info(name, notes, recipe_id):
        """Edits recipe name and notes"""
        try:
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                raise ValueError(f"No recipe matching id #: {recipe_id}")
            if name:
                recipe.name = name
            if notes:
                recipe.notes = notes
        except Exception as e:
            raise type(e)(f"Failed to process_edit_recipe_info: {e}") from e

    @staticmethod
    def process_edit_ingredients(ingredients, recipe_id):
        """Edits recipe's ingredients by modifying Ingredient association 
        or creating a new association for new ingredient"""
        try:
            for ingredient in ingredients:
                item = ingredient.get("item")
                amount = ingredient.get("amount")
                unit = ingredient.get("unit")
                if not item and not amount and not unit:
                    raise ValueError("No values in ingredient components to edit") 

                quantity_amount_id = amount["id"] if amount else None
                quantity_unit_id = unit["id"] if unit else None
                item_id = item["id"] if item else None

                if ingredient["id"]:
                    recipe_ingredient = Ingredient.query.get(
                        ingredient["id"])
                    if not recipe_ingredient:
                        raise NotFound(f"No ingredient matching id #: {ingredient['id']}")
                    
                    if amount:
                        recipe_ingredient.quantity_amount_id = quantity_amount_id
                    if unit:
                        recipe_ingredient.quantity_unit_id = quantity_unit_id
                    if item:
                        recipe_ingredient.item_id = item_id
                else:
                    RecipeIngredientRepo.create_ingredient(
                        recipe_id=recipe_id,
                        item_id=item_id,
                        quantity_unit_id=quantity_unit_id,
                        quantity_amount_id=quantity_amount_id)
        except Exception as e:
            raise type(e)(f"Failed to process_edit_ingredients: {e}") from e

    @staticmethod
    def process_edit_instructions(instructions,recipe_id):
        """Edits recipe's instructions by modifying RecipeInstruction association"""
        try:
            for instruction in instructions:
                if instruction["associationId"]:
                    recipe_instruction = RecipeInstruction.query.get(
                        instruction["associationId"])
                    if not recipe_instruction:
                        raise NotFound(
                            f"No recipe_instruction associated to id # {instruction['associationId']}")
                    recipe_instruction.instruction_id = instruction["newId"]
                else:
                    RecipeInstructionRepo.create_entry(
                        recipe_id=recipe_id,
                        instruction_id=instruction["newId"])
        except Exception as e:
            raise type(e)(f"Failed to process_edit_instructions: {e}") from e

    @staticmethod
    def remove_recipe(recipe_id):
        """Deletes book recipe"""
        try:
            RecipeRepo.delete_recipe(recipe_id=recipe_id)
            db.session.commit()
            return {"message": "deletion successful"}
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"DeleteServices - remove_recipe error: {e}") from e
