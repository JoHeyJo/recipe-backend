from repository import *
from sqlalchemy.orm import joinedload
from services.ingredients_services import IngredientServices
from services.instructions_services import InstructionServices
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, Conflict


class RecipeServices():
    """Handles recipe view business logic"""
    @staticmethod
    def process_recipe_data(request, book_id, user_id):
        """Consolidate 'create recipe' process"""
        try:
            recipe = request["recipe"]
            notes = recipe.get("notes")
            instructions = recipe.get("instructions")
            ingredients = recipe.get("ingredients")
            highlight(("recipe_data incoming",recipe, notes, instructions, ingredients),"!")
        except Exception as e:
            raise type(e)(
                f"Failed to extract recipe data for book {book_id}: {e}") from e

        try:
            recipe_data = RecipeServices.process_recipe(
                book_id=book_id, recipe_name=recipe["name"], notes=notes, user_id=user_id)

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
            highlight(("recipe_data:", recipe_data), "!")
            return recipe_data
        except Exception as e:
            db.session.rollback()
            raise type(e)(f"Failed to process_recipe_data: {e}") from e

    @staticmethod
    def process_recipe(book_id, recipe_name, notes, user_id):
        """Adds recipes and associates new recipe to book"""
        try:
            recipe_data = RecipeRepo.create_recipe(
                name=recipe_name, notes=notes, user_id=user_id)

            RecipeBookRepo.create_entry(
                book_id=book_id, recipe_id=recipe_data["id"])

            return recipe_data
        except Exception as e:
            raise type(e)(
                f"Failed to process recipe '{recipe_name}' for book {book_id}: {e}") from e

    @staticmethod
    def process_ingredients(ingredients, recipe_id, book_id):
        """Processes ingredient components creating an ingredient and associates each ingredient to recipe"""
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
                instructions=instructions, recipe_id=recipe_id)

            if not instructions_data:
                raise ValueError(
                    f"No instructions data returned for book id: {book_id}")

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
                    instances=recipe_instance.instructions)
                recipe_build["instructions"] = instructions

                ingredients = IngredientServices.build_ingredients(
                    instance=recipe_instance)
                recipe_build["ingredients"] = ingredients

                complete_recipes.append(recipe_build)
            return complete_recipes
        except Exception as e:
            raise type(e)(f"RecipeServices - build_recipes error: {e}") from e

    @staticmethod
    def build_recipe(recipe_id):
        """Builds individual recipes"""
        try:
            recipe = RecipeRepo.query_recipe(recipe_pk=recipe_id)
            instructions = InstructionServices.build_instructions(
                instances=recipe.instructions)
            ingredients = IngredientServices.build_ingredients(
                instance=recipe.ingredients)
            return {
                "is_owned_by": recipe.created_by_id,
                "id": recipe.id,
                "created_by_id": recipe.created_by_id,
                "name": recipe.name,
                "ingredients": ingredients,
                "instructions": instructions,
                "notes": recipe.notes
            }
        except Exception as e:
            raise type(e)(f"RecipeServices - build_recipe error: {e}") from e

    @staticmethod
    def process_edit(user_id, data, recipe_id):
        """Consolidates recipe edit process"""
        highlight(("edit data:", data), "!")
        if user_id is not data.get("created_by_id"):
            raise Forbidden("Not authorized to make edits")
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
                    raise ValueError(
                        "No values in ingredient components to edit")

                quantity_amount_id = amount["id"] if amount else None
                quantity_unit_id = unit["id"] if unit else None
                item_id = item["id"] if item else None

                if ingredient["id"]:
                    recipe_ingredient = Ingredient.query.get(
                        ingredient["id"])
                    if not recipe_ingredient:
                        raise NotFound(
                            f"No ingredient matching id #: {ingredient['id']}")

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
    def process_edit_instructions(instructions, recipe_id):
        """Edits recipe's instructions by - either modifying existing 
        instruction or creating a new one"""
        highlight(("instructions:", instructions), "!")
        #check if instruction needs to be replaced or created
        # replaced if there is an old id
        # created if there is no old id
        # replace instruction 
            # I need the instruction association and replace instruction id
        # create addition instruction
            # simply create new association 
        try:
            for instruction in instructions:
                if instruction["oldId"]:
                    instance = RecipeInstructionRepo.query_recipe_instruction(
                        recipe_id=recipe_id, instruction_id=instruction["newId"])
                    
                    instance.instruction_id = instruction["newId"]

                else:
                    RecipeInstructionRepo.create_entry(
                        recipe_id=recipe_id,
                        instruction_id=instruction["newId"])
        except Exception as e:
            raise type(e)(f"Failed to process_edit_instructions: {e}") from e

    @staticmethod
    def process_recipe_share(auth_id, recipient, recipe_id):
        """Process sharing user recipe with recipient"""
        recipient = UserRepo.query_user_name(user_name=recipient)
        recipe = RecipeRepo.query_recipe(recipe_pk=recipe_id)
        recipe_build = RecipeServices.build_recipe(recipe_id=recipe_id)

        if not recipient:
            return {"message": "User not found", "error": "Not Found", "code": 404}
        if auth_id == recipient.id:
            return {"message": "Why are you sharing this with yourself???",
                    "error": "BadRequest", "code": 400}
        if not recipe.is_owned_by(auth_id):
            return {"message": "This is not yours to share...",
                    "error": "Forbidden", "code": 403}
        try:
            message = RecipeServices.facilitate_recipe_link_creation(
                recipient=recipient, shared_id=recipe_id)

            if not message:
                db.session.rollback()
                return {"message": "Recipe already shared with user.",
                        "error": "Conflict", "code": 409}

            highlight(message, "!")
            db.session.commit()
            return {**message, "recipe": recipe_build}
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"Failed to process_recipe_share error: {e}") from e

    @staticmethod
    def facilitate_recipe_link_creation(recipient, shared_id):
        """"Distributes recipe data to corresponding function"""

        default_book_id = recipient.default_book_id
        book = BookRepo.query_user_book_by_pk(default_book_id)

        if not default_book_id:
            return RecipeServices.share_recipe_no_default_book(
                recipient=recipient, shared_recipe_id=shared_id)

        if book.book_type.value == "standard":
            return RecipeServices.share_recipe_standard_default_book(
                recipient=recipient, shared_recipe_id=shared_id)

        if book.book_type.value == "shared_inbox":
            return RecipeServices.share_recipe_shared_default_book(
                recipient=recipient, shared_book_id=shared_id)

        return {"message": "Nothing to process - try your request again.",
                "error": "Unknown", "code": 500}

    @staticmethod
    def share_recipe_no_default_book(recipient, shared_recipe_id):
        """User shares recipe with Recipient that has no default book assigned"""
        response = RecipeServices.fetch_shared_link(
            recipient_id=recipient.id, shared_recipe_id=shared_recipe_id)

        if not response:
            return

        message = RecipeServices.share_recipe(
            share_inbox_id=response.book_id, recipe_id=shared_recipe_id, recipient_id=recipient.id)

        # Assign Shared Recipe as default book
        recipient.default_book_id = response.book_id

        return message

    @staticmethod
    def share_recipe_standard_default_book(recipient, shared_recipe_id):
        """User shares recipe with Recipient that has STANDARD default book"""
        response = RecipeServices.fetch_shared_link(
            recipient_id=recipient.id, shared_recipe_id=shared_recipe_id)

        if not response:
            return

        message = RecipeServices.share_recipe(
            share_inbox_id=response.book_id, recipe_id=shared_recipe_id, recipient_id=recipient.id)

        return message

    @staticmethod
    def share_recipe_shared_default_book(recipient, shared_recipe_id):
        """User shares recipe with Recipient that has SHARED default book"""
        response = RecipeServices.fetch_shared_link(
            recipient_id=recipient.id, shared_recipe_id=shared_recipe_id)

    @staticmethod
    def fetch_shared_link(recipient_id, shared_recipe_id):
        """Queries shared link. Create if necessary and return link if not already shared"""
        shared_link = UserBookRepo.query_shared_book(recipient_id=recipient_id)
        if not shared_link:
            shared_book = BookRepo.create_book(title="Shared Recipes",
                                               description="Inbox: Recipes shared by others",
                                               book_type=BookType.shared_inbox)
            shared_link = UserBookRepo.create_entry(
                user_id=recipient_id, book_id=shared_book["id"])

        is_recipe_shared = RecipeBookRepo.does_recipe_exist_in_shared_inbox(
            shared_link_id=shared_link.book_id, shared_recipe_id=shared_recipe_id)

        highlight(("is_recipe_shared:", is_recipe_shared), "!")
        highlight(("shared_link:", shared_link), "!")

        return is_recipe_shared or shared_link

    @staticmethod
    def remove_recipe(auth_id, recipe_id, data):
        """Deletes book recipe"""
        if auth_id is not int(data["createdById"]):
            raise Forbidden("Not authorized to delete!")
        try:
            RecipeRepo.delete_recipe(recipe_id=recipe_id)
            db.session.commit()
            return {"message": "deletion successful"}
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"Failed to remove_recipe error: {e}") from e

    @staticmethod
    def remove_shared_recipe(authed_id, recipe_id, book_id):
        """Verifies shared recipe belongs to user's shared book. Then deletes association"""
        user_book = UserBookRepo.query_user_book(
            book_id=book_id, user_id=authed_id)

        if not user_book:
            raise NotFound("Not found")
        is_book_type_shared = user_book.book.book_type

        if not is_book_type_shared:
            raise ForbiddenError("Forbidden request")

        try:
            response = RecipeBookRepo.remove_book_association(
                book_id=book_id, recipe_id=recipe_id)
            db.session.commit()
            return response
        except Exception as e:
            db.session.rollback()
            raise type(e)(f"Failed to remove_shared_recipe error: {e}") from e

    @staticmethod
    def share_recipe(share_inbox_id, recipe_id, recipient_id):
        """Associate user's shared recipe to recipients 'Shared Recipes' book"""
        # take a look at this return object
        res = RecipeBookRepo.create_entry(
            book_id=share_inbox_id, recipe_id=recipe_id)
        highlight(("RES:", res), "!")
        book_with_role = BookRepo.build_book(
            user_id=recipient_id, book_id=share_inbox_id)

        return {"message": "Recipe successfully shared!",
                "recipient_id": recipe_id,
                "code": 200, "payload": book_with_role
                }
