from repository import *
from sqlalchemy.orm import selectinload
from services.ingredients_services import IngredientServices
from services.instructions_services import InstructionServices
from services.user_services import UserServices
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, Conflict
from models import BookType
from repository import BookRepo


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
        """Consolidate recipe parts: recipe info, instructions, ingredients - returns to client list
        of readable recipes.
        My code before AI refactor d1072a4552ba6f0aaad85bbb5c3eaf39ca9c82f7"""
        complete_recipes = []
        try:
            book = BookRepo.query_user_book_by_pk(book_pk=book_id)
            if book is None:
                raise ValueError(f"No book found with ID {book_id}")

            stmt = (
                db.select(Recipe)
                .join(RecipeBook, RecipeBook.recipe_id == Recipe.id)
                .where(RecipeBook.book_id == book_id)
                .options(
                    selectinload(Recipe.instructions),
                    selectinload(Recipe.ingredients).selectinload(
                        Ingredient.amount),
                    selectinload(Recipe.ingredients).selectinload(Ingredient.unit),
                    selectinload(Recipe.ingredients).selectinload(Ingredient.item),
                )
                .order_by(Recipe.name)
            )
            recipe_instances = db.session.execute(stmt).scalars().all()

            for recipe_instance in recipe_instances:
                recipe_build = Recipe.serialize(recipe_instance)

                recipe_build["instructions"] = InstructionServices.build_instructions(
                    instances=recipe_instance.instructions)
                
                recipe_build["ingredients"] = IngredientServices.build_ingredients(
                    instances=recipe_instance.ingredients)
                
                complete_recipes.append(recipe_build)
                
            return complete_recipes
        except Exception as e:
            raise type(e)(f"RecipeServices - build_recipes error: {e}") from e
        

    @staticmethod
    def build_recipe(recipe_id):
        """Builds individual recipes"""
        try:
            recipe = RecipeRepo.query_recipe(recipe_pk=recipe_id, eager=True)
            instructions = InstructionServices.build_instructions(
                instances=recipe.instructions)
            ingredients = IngredientServices.build_ingredients(
                instances=recipe.ingredients)
            return {
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
    def process_edit(user_id, data, book_id, recipe_id):
        """Consolidates recipe edit process. Currently request recipe return after editing is done
        instead of building recipe from individual recipe parts. This requires two separate patterns to consider"""
        UserServices.check_book_privileges(
            book_id=book_id, auth_id=user_id, user_id=data.get("created_by_id"))
        try:
            name = data.get("name")
            ingredients = data.get("ingredients")
            instructions = data.get("instructions")
            notes = data.get("notes")

        except Exception as e:
            raise type(e)(
                f"Failed to extract recipe edit data for recipe {recipe_id}: {e}") from e
        
        try:
            # can these three functions be consolidated into one after query recipe refactor?
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
            edited_recipe = RecipeServices.build_recipe(recipe_id=recipe_id)
            highlight("edited_recipe", edited_recipe)
            return edited_recipe
        except Exception as e:
            db.session.rollback()
            raise type(e)(f"Failed to process_edit: {e}") from e

    @staticmethod
    def process_edit_recipe_info(name, notes, recipe_id):
        """Edits recipe name and notes"""
        try:
            recipe = RecipeRepo.query_recipe(recipe_pk=recipe_id, eager=False)
            if not recipe:
                raise ValueError(f"No recipe matching id #: {recipe_id}")
            if name:
                recipe.name = name
            if notes:
                recipe.notes = notes
            return recipe
        except Exception as e:
            raise type(e)(f"Failed to process_edit_recipe_info: {e}") from e

    @staticmethod
    def process_edit_ingredients(ingredients, recipe_id):
        """Edits recipe's ingredients by modifying Ingredient association 
        or creating a new association for new ingredient. Existing ingredients are fetched in one batch."""
        try:
            edit_ids = [ing["id"] for ing in ingredients if ing["id"]]
            existing = {
                ing.id: ing
                for ing in IngredientsRepo.query_ingredients(edit_ids)
            }

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

                if item_id is None:
                    raise ValueError("Ingredient must have an item name.")

                if ingredient["id"]:
                    recipe_ingredient = existing.get(ingredient["id"])

                    if not recipe_ingredient:
                        raise NotFound(
                            f"No ingredient matching id #: {ingredient['id']}")

                    is_altered = recipe_ingredient.item_id != item_id

                    if amount:
                        recipe_ingredient.quantity_amount_id = quantity_amount_id
                    if unit:
                        recipe_ingredient.quantity_unit_id = quantity_unit_id
                    if item and is_altered:
                        recipe_ingredient.item_id = item_id
                else:
                    RecipeIngredientRepo.create_ingredient(
                        recipe_id=recipe_id,
                        item_id=item_id,
                        quantity_unit_id=quantity_unit_id,
                        quantity_amount_id=quantity_amount_id)
            return ingredients
        except Exception as e:
            raise type(e)(f"Failed to process_edit_ingredients: {e}") from e

    @staticmethod
    def process_edit_instructions(instructions, recipe_id):
        """Edits recipe's instructions - modifying existing instruction or 
        creating a new one"""
        try:
            for instruction in instructions:
                if instruction["oldId"]:
                    instance = RecipeInstructionRepo.query_recipe_instruction(
                        recipe_id=recipe_id, instruction_id=instruction["oldId"])

                    instance.instruction_id = instruction["newId"]
                if instruction["oldId"] is None:
                    RecipeInstructionRepo.create_entry(
                        recipe_id=recipe_id,
                        instruction_id=instruction["newId"])
            return RecipeInstructionRepo.query_recipe_instructions(
                recipe_id=recipe_id)
        except Exception as e:
            raise type(e)(f"Failed to process_edit_instructions: {e}") from e

    @staticmethod
    def process_recipe_share(auth_id, recipient, recipe_id):
        """Process sharing user recipe with recipient"""
        recipient = UserRepo.query_user_name(user_name=recipient)
        recipe = RecipeRepo.query_recipe(recipe_pk=recipe_id, eager=False)
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
            response = RecipeServices.facilitate_recipe_link_creation(
                recipient=recipient, shared_id=recipe_id)

            if response is None:
                db.session.rollback()
                return {"message": "Recipe already shared with user.",
                        "error": "Conflict", "code": 409}

            db.session.commit()
            return {**response, "recipe": recipe_build}
        except Exception as e:
            db.session.rollback()
            raise type(e)(
                f"Failed to process_recipe_share error: {e}") from e

    @staticmethod
    def facilitate_recipe_link_creation(recipient, shared_id):
        """"Distributes recipe data to corresponding function based on if user has
        no default book, standard default book, or a shared_inbox default book"""
        default_book_id = recipient.default_book_id

        if default_book_id is None:
            return RecipeServices.share_recipe_no_default_book(
                recipient=recipient, shared_recipe_id=shared_id)

        book = BookRepo.query_user_book_by_pk(default_book_id)
        if book.book_type == BookType.standard:
            return RecipeServices.share_recipe_standard_default_book(
                recipient=recipient, shared_recipe_id=shared_id)

        if book.book_type == BookType.shared_inbox:
            return RecipeServices.share_recipe_shared_default_book(shared_book_id=book.id,
                                                                   recipient=recipient, shared_recipe_id=shared_id)

        return {"message": "Nothing to process - try your request again.",
                "error": "Unknown", "code": 500}

    @staticmethod
    def share_recipe_no_default_book(recipient, shared_recipe_id):
        """User shares recipe with Recipient that has NO DEFAULT book """
        shared_link_response = RecipeServices.fetch_shared_link(
            recipient_id=recipient.id, shared_recipe_id=shared_recipe_id)

        if shared_link_response is None:
            return None

        response = RecipeServices.share_recipe(
            share_inbox_id=shared_link_response["user_book"].book_id, recipe_id=shared_recipe_id, recipient_id=recipient.id)

        # Assign Shared Recipe as default book
        recipient.default_book_id = shared_link_response["user_book"].book_id

        if shared_link_response["isInstantiation"] is False:
            response["payload"] = None

        return response

    @staticmethod
    def share_recipe_standard_default_book(recipient, shared_recipe_id):
        """User shares recipe with Recipient that has STANDARD default book"""
        shared_link_response = RecipeServices.fetch_shared_link(
            recipient_id=recipient.id, shared_recipe_id=shared_recipe_id)

        if shared_link_response is None:
            return None

        response = RecipeServices.share_recipe(
            share_inbox_id=shared_link_response["user_book"].book_id,
            recipe_id=shared_recipe_id, recipient_id=recipient.id)

        if shared_link_response["isInstantiation"] is False:
            response["payload"] = None

        return response

    @staticmethod
    def share_recipe_shared_default_book(shared_book_id, recipient, shared_recipe_id):
        """User shares recipe with Recipient that has SHARED default books"""
        is_recipe_shared = RecipeBookRepo.does_recipe_exist_in_shared_inbox(
            shared_book_id=shared_book_id, shared_recipe_id=shared_recipe_id)

        if is_recipe_shared:
            return None

        response = RecipeServices.share_recipe(
            share_inbox_id=shared_book_id, recipe_id=shared_recipe_id, recipient_id=recipient.id)

        response["payload"] = None

        return response

    @staticmethod
    def fetch_shared_link(recipient_id, shared_recipe_id):
        """Queries user book link. Create and associate to user if necessary.
        Check if recipe is already shared. Return None or user book link IF it's created"""
        link = {"user_book": None, "isInstantiation": False}
        link["user_book"] = UserBookRepo.query_user_shared_inbox(
            recipient_id=recipient_id)

        if link["user_book"] is None:
            shared_book = BookRepo.create_book(title="Shared Recipes",
                                               description="Inbox: Recipes shared by others",
                                               book_type=BookType.shared_inbox)

            link["user_book"] = UserBookRepo.create_entry(
                user_id=recipient_id, book_id=shared_book["id"])
            link["isInstantiation"] = True

        is_recipe_shared = RecipeBookRepo.does_recipe_exist_in_shared_inbox(
            shared_book_id=link["user_book"].book_id, shared_recipe_id=shared_recipe_id)

        if is_recipe_shared:
            return None

        return link

    @staticmethod
    def remove_recipe(auth_id, book_id, recipe_id, data):
        """Deletes book recipe"""
        UserServices.check_book_privileges(
            book_id=book_id, auth_id=auth_id, user_id=int(data["createdById"]))
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
        user_book = UserBookRepo.query_users_books(
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
        """Associate user's shared recipe to recipients 'Shared Recipes' book.
        Build and return book object"""
        # take a look at this return object
        RecipeBookRepo.create_entry(
            book_id=share_inbox_id, recipe_id=recipe_id)

        book_with_role = BookRepo.build_book_with_query(
            user_id=recipient_id, book_id=share_inbox_id)

        return {"message": "Recipe successfully shared!",
                "recipient_id": recipient_id,
                "code": 200, "payload": book_with_role
                }

    @staticmethod
    def copy_recipe(request, book_id, user_id):
        """Copy recipe to Recipient"""
        recipe = request["recipe"]

        is_authed = RecipeServices.is_authed_to_copy(
            user_id=user_id, recipe_id=recipe.get("id"), book_id=book_id)

        if is_authed:
            RecipeServices.process_recipe_data(
                request=request, book_id=book_id, user_id=user_id)
            return RecipeServices.build_recipes(book_id=book_id)
        # Data sent by client does not match internal data
        raise BadRequest("Unable to process request")

    @staticmethod
    def is_authed_to_copy(user_id, recipe_id, book_id):
        """Checks if recipe exists in user's shared inbox and if user has access to targeted book"""
        user_books = BookRepo.query_user_books_instances(user_id=user_id)

        has_access_to_recipe = False
        is_book_owner = False

        for book in user_books:
            if book.book_type.value == "shared_inbox":
                if book.id == book_id:
                    raise Conflict(
                        "You cannot share with your own 'Shared Books' recipe book.")
                has_access_to_recipe = any(
                    recipe.id == recipe_id for recipe in book.recipes)
            if book.id == int(book_id):
                is_book_owner = True

            if has_access_to_recipe and is_book_owner:
                return True

        return False
