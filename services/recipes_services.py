from repository import *


class RecipeService():
    """Handles recipe view business logic"""
    @staticmethod
    def process_recipe_data(data, user_id, book_id):
        """Consolidate 'create recipe' process"""
        try:
            recipe = data["recipe"]
            notes = recipe.get("notes")
            instructions = recipe.get("instructions")
            ingredients = recipe.get("ingredients")
        except Exception as e:
            raise ValueError(
                f"Failed to extract recipe data for book {book_id}: {e}")

        try:

            recipe_data = RecipeService.process_recipe(
                book_id=book_id, recipe_name=recipe["name"], notes=notes)
            
            if ingredients:
                recipe_data["ingredients"] = RecipeService.process_ingredients(
                    ingredients=ingredients, recipe_id=recipe_data["recipe_id"])
                
            if instructions:
                recipe_data["instructions_data"] = RecipeService.process_instructions(
                    recipe_id=recipe_data["recipe_id"], instructions=instructions, book_id=book_id)

            return recipe_data
        except Exception as e:
            highlight(e, "!")
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
            highlight(e, "!")
            raise ValueError(
                f"Failed to process recipe '{recipe_name}' for book {book_id}: {e}")

    @staticmethod
    def process_ingredients(ingredients, recipe_id):
        """Adds ingredients and associates each ingredient to recipe"""
        try:
            ingredients_data = IngredientsRepo.process_ingredients(
                ingredients=ingredients)
            if not ingredients_data:
                raise ValueError(
                    f"No ingredients data returned for recipe {recipe_id}")
            highlight(ingredients_data, "@")
            for ingredient in ingredients_data:
                RecipeIngredientRepo.create_recipe(
                    recipe_id=recipe_id,
                    item_id=ingredient["item"]['id'],
                    quantity_amount_id=ingredient["amount"]['id'],
                    quantity_unit_id=ingredient["unit"]['id'])

            return ingredients_data
        except Exception as e:
            highlight(e, "!")
            raise ValueError(
                f"Failed to process ingredients for recipe {recipe_id}: {e}")

    @staticmethod
    def process_instructions(recipe_id, instructions, book_id):
        """Adds instructions and associates each instruction to book"""
        try:
            instructions_data = InstructionRepo.process_instructions(
                instructions=instructions)

            if not instructions_data:
                raise ValueError(
                    f"No instructions data returned for book {book_id}")

            for instruction in instructions_data:
                BookInstructionRepo.create_entry(
                    book_id=book_id, instruction_id=instruction["id"])
                RecipeInstructionRepo.create_entry(
                    recipe_id=recipe_id, instruction_id=instruction["id"])

            return instructions_data
        except Exception as e:
            highlight(e, "!")
            raise ValueError(
                f"Failed to process_instructions for book {book_id}: {e}")

    @staticmethod
    def build_recipes(book_id):
        """Consolidate recipe components"""
        recipes = Book.query.get()
        # for recipe in recipes:
        #     instructions = recipe["instructions_data"]
        #     ingredients = recipe["ingredients"]
        #     r = {"id":recipe["id"], "name": recipe["name"], "notes": recipe["notes"],
        #          "ingredients": ingredients, "instructions": instructions}
        #     full_recipes.append(r)


[{'id': 1,
  'name': 'Manhattan North',
  'notes': '{"It\'s great on the rocks on a hot day!"}',
  'ingredients': [< RecipeIngredient(id=1, recipe_id=1, item_id=1, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 33, 12, 486079)) > ,
                   < RecipeIngredient(id=2, recipe_id=1, item_id=2, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 33, 12, 490486)) >,
                   < RecipeIngredient(id=3, recipe_id=1, item_id=3, quantity_unit_id=1, quantity_amount_id=2, created_at=datetime.datetime(2024, 10, 14, 15, 33, 12, 492152)) >],
  'instructions': []},
 {'id': 2,
  'name': 'Manhattan North',
  'notes': '{"It\'s great on the rocks on a hot day!"}',
  'ingredients': [],
  'instructions': []},
 {'id': 3,
  'name': 'Manhattan North',
  'notes': '{"It\'s great on the rocks on a hot day!"}',
  'ingredients': [< RecipeIngredient(id=4, recipe_id=3, item_id=1, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 35, 11, 779671)) > ,
                   < RecipeIngredient(id=5, recipe_id=3, item_id=1, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 35, 11, 782093)) >,
                   < RecipeIngredient(id=6, recipe_id=3, item_id=1, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 35, 11, 783419)) >],
  'instructions': []},
 {'id': 4,
  'name': 'Manhattan North',
  'notes': '{"It\'s great on the rocks on a hot day!"}',
  'ingredients': [< RecipeIngredient(id=7, recipe_id=4, item_id=1, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 37, 37, 231507)) > ,
                   < RecipeIngredient(id=8, recipe_id=4, item_id=1, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 37, 37, 234539)) >,
                   < RecipeIngredient(id=9, recipe_id=4, item_id=1, quantity_unit_id=1, quantity_amount_id=1, created_at=datetime.datetime(2024, 10, 14, 15, 37, 37, 236958)) >],
  'instructions': [< Instruction(id=1, instruction='Add ingredients over ice', created_at=datetime.datetime(2024, 10, 14, 15, 37, 37, 239374)) > ,
                    < Instruction(id=2, instruction='shake ingredients', created_at=datetime.datetime(2024, 10, 14, 15, 37, 37, 242898)) >,
                    < Instruction(id=3, instruction='strain into glass', created_at=datetime.datetime(2024, 10, 14, 15, 37, 37, 245496)) > ,
   < Instruction(id=4, instruction='garnish with cherry', created_at=datetime.datetime(2024, 10, 14, 15, 37, 37, 248208))>]}]