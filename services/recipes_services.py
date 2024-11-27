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
                    ingredients=ingredients, recipe_id=recipe_data["id"])
                
            if instructions:
                recipe_data["instructions"] = RecipeService.process_instructions(
                    recipe_id=recipe_data["id"], instructions=instructions, book_id=book_id)

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
                book_id=book_id, recipe_id=recipe_data["id"])
            
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
            for ingredient in ingredients_data:
                id = RecipeIngredientRepo.create_ingredient(
                    recipe_id=recipe_id,
                    item_id=ingredient["item"]['id'],
                    quantity_amount_id=ingredient["amount"]['id'],
                    quantity_unit_id=ingredient["unit"]['id'])
                ingredient["ingredient_id"] = id

            return ingredients_data
        except Exception as e:
            highlight(e, "!")
            raise ValueError(
                f"Failed to process ingredients for recipe {recipe_id}: {e}")

    @staticmethod
    def process_instructions(recipe_id, instructions, book_id):
        """Adds instructions and associates each instruction to book"""
        highlight(instructions,"#")
        try:
            instructions_data = InstructionRepo.process_instructions(
                instructions=instructions)

            if not instructions_data:
                raise ValueError(
                    f"No instructions data returned for book {book_id}")

            for instruction in instructions_data:
                BookInstructionRepo.create_entry(
                    book_id=book_id, instruction_id=instruction["id"])
                id = RecipeInstructionRepo.create_entry(
                    recipe_id=recipe_id, instruction_id=instruction["id"])
                instruction["instruction_id"] = id

            return instructions_data
        except Exception as e:
            highlight(e, "!")
            raise ValueError(
                f"Failed to process_instructions for book {book_id}: {e}")

    @staticmethod
    def build_recipes(book_id):
        """Consolidate recipe parts: recipe info, instructions, ingredients"""
        complete_recipes = []
        book = Book.query.get(book_id)
        recipes_instances = book.recipes
        for recipe_instance in recipes_instances:
            recipe_build = {}

            recipe = Recipe.serialize(recipe_instance)
            recipe_build.update(recipe)
            
            instructions = InstructionRepo.build_instructions(
                recipe_instance.instructions)
            recipe_build["instructions"] = instructions

            ingredients = IngredientsRepo.build_ingredients(recipe_instance)
            recipe_build["ingredients"] = ingredients
            
            complete_recipes.append(recipe_build)
        return complete_recipes
    
    @staticmethod
    def process_edit(data, recipe_id):
        """Consolidates recipe edit process"""
        try:
            name = data.get("name")
            ingredients = data.get("ingredients")
            instructions = data.get("instructions")
            notes = data.get("notes")
        except Exception as e:
            raise ValueError(
                f"Failed to extract recipe edit data for recipe {recipe_id}: {e}")
        
        try:
            if name or notes:
                recipe = Recipe.query.get(recipe_id)
                if name:
                    recipe.name = name
                if notes:
                    recipe.notes = notes
                db.session.commit()
        except Exception as e:
            highlight(e, "!")
            raise ValueError(f"Failed to process_edit - name or notes: {e}")
        
        try:
            if ingredients:
                for ingredient in ingredients:
                    recipe_ingredient = RecipeIngredient.query.get(ingredient["ingredient_id"])
                    if ingredient.get("item"):
                        recipe_ingredient.item_id = ingredient["item"]["id"]
                    if ingredient.get("amount"):
                        recipe_ingredient.quantity_amount_id = ingredient["amount"]["id"]
                    if ingredient.get("unit"):
                        recipe_ingredient.quantity_unit_id = ingredient["unit"]["id"]
            db.session.commit()
        except Exception as e:
            highlight(e, "!")
            raise ValueError(f"Failed to process_edit - ingredients: {e}")
        
        try:
            if instructions:
                for instruction in instructions:
                    None
                    # recipe_instruction = RecipeInstruction.query.get(instruction[])
        except Exception as e:
            highlight(e, "!")
            raise ValueError(f"Failed to process_edit - instructions: {e}")
        return {"msg":"edit successful"}

