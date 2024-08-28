from repository import *

class RecipeService():
  """Handles recipe view business logic"""
  @staticmethod
  def add_recipe(data):
    recipe_data = None
    # User data
    user_id = data["user_id"]
    book_id = data["book_id"]

    # Recipe data
    recipe = data["recipe"]
    recipe_name = recipe["name"]
    preparation = recipe["preparation"] or None
    notes = recipe["notes"] or None

    # Ingredient data
    ingredients = recipe["ingredients"] or None
    # ############ RECIPE CREATION ########
    # First add ingredients if applicable then add recipe
    try:
        if ingredients:
            ingredients_data = IngredientsRepo.add_ingredients(ingredients)

            recipe_data = RecipeRepo.create_recipe(
                name=recipe_name, notes=notes)
            
            instructions_data = 

            recipe_data['ingredients'] = ingredients_data

            for ingredient in recipe_data['ingredients']:
                RecipeIngredientRepo.create_recipe(
                    recipe_id=recipe_data['recipe_id'],
                    ingredient_id=ingredient['ingredient_id'],
                    quantity_amount_id=ingredient['amount_id'],
                    quantity_unit_id=ingredient['unit_id'])

            recipe_data = recipe_data
        else:
            recipe_data = RecipeRepo.create_recipe(
                name=recipe_name, notes=notes)
            recipe_data = recipe_data
            
        # ############ ADD RECIPE TO BOOK (recipes_books) ########
        RecipeBookRepo.create_entry(
            book_id=book_id, recipe_id=recipe_data["recipe_id"])
        # ############ ADD BOOK TO USER (users_books) ########
        UserBookRepo.create_entry(user_id=user_id, book_id=book_id)

        return recipe_data

    except IntegrityError as e:
        raise {"error": f"adding recipe & ingredients in add_recipe: {e}"}
