import os
from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from repository import *
from models import connect_db, db
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from dotenv import load_dotenv
from flask_cors import CORS
from exceptions import *
from services.user_services import UserServices
from services.recipes_services import RecipeServices
from services.ingredients_services import IngredientServices
from services.book_services import BookServices
from services.instructions_services import InstructionServices
from utils.error_handler import handle_error
from datetime import timedelta
from decorators.verify_user import check_user_identity
from decorators.handle_route_errors import error_handler

# Execute if app doesn't auto update code
# flask --app app.py --debug run

app = Flask(__name__)
load_dotenv()  # This loads the variables from .env into the environment
app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # change to False for production
app.config['DEBUG'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # does this auto update flask app?

debug = DebugToolbarExtension(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)

connect_db(app)
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)  # SPECIFY CORS OPTIONS FOR RESOURCES FOR DEPLOYMENT ^^^^^


@app.get("/")
@jwt_required()
def index():
    header = request.headers
    return "hello"


@app.post("/signup")
def signup():
    """Facilitates new user data, return token"""
    try:
        token = UserServices.authenticate_signup(request=request)
        return jsonify({"token": token})
    except (UsernameAlreadyTakenError, EmailAlreadyRegisteredError, SignUpError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.post("/login")
def login():
    """Validate user credentials"""
    try:
        token = UserServices.authenticate_login(request=request)
        if token:
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": "An error occurred during login"}), 500


########### USERS ###########
@app.get("/users/<user_id>")
@check_user_identity
def get_user(user_id):
    """Retrieve user associated to id"""
    try:
        return jsonify(UserServices.fetch_user(user_id=user_id))
    except Exception as e:
        return handle_error(e)

############ RECIPES ###########


@app.post("/users/<user_id>/books/<book_id>/recipes")
@check_user_identity
@error_handler
def add_recipe(user_id, book_id):
    """Consolidate recipe data. If successful recipes_ingredients record created"""
    recipe_data = RecipeServices.process_recipe_data(
        request={"recipe": request}, book_id=book_id, user_id=user_id)
    return jsonify(recipe_data), 200


@app.get("/users/<user_id>/books/<book_id>/recipes")
def get_book_recipes(user_id, book_id):
    """Return recipes associated to user's book"""
    try:
        recipes = RecipeServices.build_recipes(book_id=book_id)
        return jsonify(recipes)
    except Exception as e:
        return handle_error(e)


@app.patch("/users/<user_id>/books/<book_id>/recipes/<recipe_id>")
def update_user_recipe(user_id, book_id, recipe_id):
    """Facilitate editing of recipe and records associated to book"""
    try:
        recipe = RecipeServices.process_edit(
            data=request.json, recipe_id=recipe_id)
        return jsonify(recipe)
    except Exception as e:
        return handle_error(e)


@app.delete("/users/<user_id>/books/<book_id>/recipes/<recipe_id>")
def get_delete_recipe(user_id, book_id, recipe_id):
    """Facilitate deletion of recipe record associated to user"""
    try:
        RecipeRepo.delete_recipe(recipe_id=recipe_id)
        return jsonify({"message": "deletion successful"})
    except Exception as e:
        return handle_error(e)


########### BOOKS ###########


@app.post("/users/<user_id>/books")
def add_book(user_id):
    """Facilitates creation of book"""
    title = request.json["title"]
    description = request.json["description"]
    book_data = {"title": title, "description": description}
    try:
        book_data = BookServices.process_new_book(
            book_data=book_data, user_id=user_id)
        return jsonify(book_data), 200
    except IntegrityError as e:
        return jsonify({"error": f"create_book error{e}"}), 400


@app.get("/users/<user_id>/books")
@check_user_identity
def get_user_books(user_id):
    """Returns all books associated with user"""
    books = BookRepo.get_user_books(user_id=user_id)
    return jsonify(books)


###########  COMPONENT OPTIONS = {amount, unit, item} = INGREDIENT ###########

@app.post("/users/<user_id>/books/<book_id>/ingredients/<component>")
@check_user_identity
def add_book_ingredient(user_id, book_id, component):
    """Facilitates creation of book's component option"""
    try:
        return IngredientServices.post_component_option(
            component=component, option=request.json, book_id=book_id)
    except IntegrityError as e:
        return jsonify({"error": f"add_book_ingredient error{e}"}), 400


@app.post("/users/<user_id>/books/<book_id>/components/<component>/options/<option_id>")
@check_user_identity
def add_option_association(user_id, book_id, component, option_id):
    """Facilitates association of user option to book"""
    try:
        IngredientServices.create_option_association(
            component=component, book_id=book_id, option_id=option_id)
        return jsonify({"message":
                        f"Successful association of option {option_id} to book {book_id}!"})
    except IntegrityError as e:
        return jsonify({"error": f"add_option_association error{e}"}), 400


@app.get("/ingredients/<ingredient>")
@jwt_required()
def get_ingredients(ingredient):
    """Facilitates retrieval of ALL options of ingredient components"""
    try:
        ingredients = IngredientServices.fetch_components_options(ingredient)
        return jsonify(ingredients)
    except IntegrityError as e:
        return jsonify({"error": f"get_ingredients error{e}"}), 400


@app.get("/users/<user_id>/ingredients/components")
@check_user_identity
def get_user_ingredients(user_id):
    """Facilitates retrieval of components options associated to User"""
    try:
        return IngredientServices.fetch_user_components_options(user_id=user_id)
    except IntegrityError as e:
        return jsonify({"error": f"get_user_ingredients error{e}"}), 400


@app.get("/users/<user_id>/books/<book_id>/ingredients/components")
@check_user_identity
def get_book_ingredient_components(user_id, book_id):
    """Facilitates retrieval of components options associated to Book"""
    try:
        return IngredientServices.fetch_book_components_options(book_id=book_id)
    except IntegrityError as e:
        return jsonify({"error": f"get_book_ingredients error{e}"}), 400


@app.post("/ingredients/<ingredient>")
# should identity be checked here?
# def add_ingredient(ingredient):
#     """Facilitates creation of ingredient"""
#     value = request.json
#     try:
#         ingredient = IngredientServices.add_ingredient(
#             option=ingredient, value=value)
#         return jsonify(ingredient)
#     except IntegrityError as e:
#         return jsonify({"error": f"add_ingredient error{e}"}), 400
########### INSTRUCTIONS ###########
@app.post("/users/<user_id>/books/<book_id>/instructions")
@check_user_identity
def add_instruction(user_id, book_id):
    """Facilitates creation of instruction"""
    instruction = request.json["instruction"]
    try:
        instruction = InstructionRepo.create_instruction(
            instruction=instruction, book_id=book_id)
        return jsonify(instruction)
    except IntegrityError as e:
        return jsonify({"error": f"add_instruction error{e}"}), 400


@app.post("/users/<user_id>/books/<book_id>/instructions/<instruction_id>")
@check_user_identity
def add_instruction_association(user_id, book_id, instruction_id):
    """Facilitates association of user instruction to book"""
    try:
        InstructionServices.create_instruction_association(
            book_id=book_id, instruction_id=instruction_id)
        return jsonify({"message":
                        f"Successful association of instruction {instruction_id} to book {book_id}!"})
    except IntegrityError as e:
        return jsonify({"error": f"add_instruction_association error{e}"}), 400


@app.get("/instructions")
@jwt_required()
def get_instructions():
    """Facilitates retrieval of instructions"""
    try:
        instructions = InstructionRepo.get_instructions()
        return jsonify(instructions)
    except IntegrityError as e:
        return jsonify({"error": f"/instructions - get_instructions error{e}"}), 400


@app.get("/users/<user_id>/instructions")
@check_user_identity
def get_user_instructions(user_id):
    """Facilitates retrieval of user instructions"""
    try:
        instructions = InstructionServices.fetch_user_instructions(
            user_id=user_id)
        return jsonify(instructions)
    except IntegrityError as e:
        return jsonify({"error": f"/instructions - get_user_instructions error{e}"}), 400


@app.get("/users/<user_id>/books/<book_id>/instructions")
@check_user_identity
def get_book_instructions(user_id, book_id):
    """Facilitates retrieval of book instructions"""
    try:
        has_access = InstructionServices.check_book_access(
            user_id=user_id, book_id=book_id)
        if has_access:
            instructions = InstructionServices.fetch_book_instructions(
                book_id=book_id)
            return jsonify(instructions)
        else:
            return jsonify({"message": "user does not have access to book"})
    except IntegrityError as e:
        return jsonify({"error": f"/instructions - get_book_instructions error{e}"}), 400

################################################################################


def setup_app_context():
    """Function to setup app context. Allows database access via IPython shell"""
    app.app_context().push()
