from repository import *


class RecipeService():
    """Handles recipe view business logic"""
    @staticmethod
    def add_recipe(data, current_book_id):
        """"""
        highlight(data, "@")
        recipe_data = None
        # User data
        user_id = data["user_id"]

        # Recipe data
        recipe = data["recipe"]
        recipe_name = recipe["name"]
        notes = recipe["notes"] or None
        instructions = recipe["instructions"] or None

        # Ingredient data
        ingredients = recipe["ingredients"] or None

        # ############ RECIPE CREATION ########
        # First add ingredients if applicable then add recipe
        highlight(data, "2")
        try:
            # recipe_data = RecipeRepo.create_recipe(
            #     name=recipe_name, notes=notes)
            # if ingredients:
            #     ingredients_data = IngredientsRepo.process_ingredients(
            #         ingredients=ingredients)

            # recipe_data['ingredients'] = ingredients_data
            # associating ingredients to recipe
            # for ingredient in recipe_data['ingredients']:
            #     RecipeIngredientRepo.create_recipe(
            #         recipe_id=recipe_data["recipe_id"],
            #         ingredient_id=ingredient["ingredient"]['id'],
            #         quantity_amount_id=ingredient["amount"]['id'],
            #         quantity_unit_id=ingredient["unit"]['id'])

            # if instructions:
            #     instructions_data = InstructionRepo.process_instructions(
            #         instructions=instructions)
            #     recipe_data["instructions_data"] = instructions_data

            # # # ############ ADD RECIPE TO BOOK (recipes_books) ########
            # RecipeBookRepo.create_entry(
            #     book_id=current_book_id, recipe_id=recipe_data["recipe_id"])
            # # ############ ADD BOOK TO USER (users_books) ########
            # UserBookRepo.create_entry(user_id=user_id, book_id=current_book_id)
            # # ############ ADD INSTRUCTION TO BOOK (books_instructions) ########
            # for instruction in instructions_data:
                # BookInstructionRepo.create_entry(
                    # book_id=current_book_id, instruction_id=instruction["id"])

            return recipe_data

        except Exception as e:
            raise {"error": f"adding recipe & ingredients in add_recipe: {e}"}

    @staticmethod
    def process_recipe_data(data, user_id, book_id):
        """Consolidate multi-step process to create a recipe"""
        try:
            recipe_data = None

            recipe = data["recipe"]
            notes = recipe["notes"] or None
            instructions = recipe["instructions"] or None
            ingredients = recipe["ingredients"] or None
        except Exception as e:
            raise ValueError(f"Failed to extract recipe data: {e}")

        try:
            recipe_data = RecipeService.process_recipe(
                    book_id=book_id, recipe_name=recipe["name"])

            if ingredients:
                recipe_data["ingredients"] = RecipeService.process_ingredients(
                    ingredients=ingredients, recipe_id=recipe_data["recipe_id"])

            if instructions:
                recipe_data["instructions_data"] = RecipeService.process_instructions(
                    instructions=instructions, book_id=book_id)
        except Exception as e:
            raise ValueError(f"Failed to process_recipe: {e}")


    @staticmethod
    def process_recipe(book_id, recipe_name, notes):
        """Adds recipes and associates new recipe to book"""
        try:
            recipe_data = RecipeRepo.create_recipe(
                name=recipe_name, notes=notes)

            RecipeBookRepo.create_entry(
                book_id=book_id, recipe_id=recipe_data["recipe_id"])

            return recipe_data
        except Exception as e:
            raise ValueError(f"Failed to process_recipe: {e}")

    @staticmethod
    def process_ingredients(ingredients, recipe_id):
        """Adds ingredients and associates each ingredient to recipe"""
        try:
            ingredients_data = IngredientsRepo.process_ingredients(
                ingredients=ingredients)

            for ingredient in ingredients_data:
                RecipeIngredientRepo.create_recipe(
                    recipe_id=recipe_id,
                    ingredient_id=ingredient["ingredient"]['id'],
                    quantity_amount_id=ingredient["amount"]['id'],
                    quantity_unit_id=ingredient["unit"]['id'])

            return ingredients_data
        except Exception as e:
            raise ValueError(f"Failed to process_ingredients: {e}")

    @staticmethod
    def process_instructions(instructions, book_id):
        """Adds instructions and associates each instruction to book"""
        try:
            instructions_data = InstructionRepo.process_instructions(
                instructions=instructions)

            for instruction in instructions_data:
                BookInstructionRepo.create_entry(
                    book_id=book_id, instruction_id=instruction["id"])
            return instructions_data
        except Exception as e:
            raise ValueError(f"Failed to process_instructions: {e}")
