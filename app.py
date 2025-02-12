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
from services.recipes_services import RecipeService
from services.ingredients_services import IngredientService
from services.book_services import BookService
from services.instructions_services import InstructionService
from utils.error_handler import handle_error
from datetime import timedelta
from utils.verify_user import check_user_identity

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
    """Facilitates new user data to User Repo, return token"""
    user_name = request.json["userName"]
    first_name = request.json["firstName"]
    last_name = request.json["lastName"]
    password = request.json["password"]
    email = request.json["email"]
    try:
        token = UserRepo.signup(user_name, first_name,
                                last_name, email, password)
        return jsonify({"token": token})
    except UsernameAlreadyTakenError as e:
        # Handle username already taken error
        return jsonify({"error": str(e)}), 400
    except EmailAlreadyRegisteredError as e:
        # Handle email already taken error
        return jsonify({"error": str(e)}), 400
    except SignUpError as e:
        # Handle general sign-up error
        return jsonify({"error": "Sign up error: An unexpected error occurred."}), 500
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.post("/login")
def login():
    """Validate user credentials"""

    user_name = request.json["userName"]
    password = request.json["password"]
    try:
        token = UserRepo.authenticate(user_name, password)
        if token:
            return jsonify({"token": token})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except IntegrityError as e:
        return jsonify({"error": f"login error: {e}"}), 400


########### USERS ###########
@app.get("/users/<user_id>")
@check_user_identity
def get_user(user_id):
    """Retrieve user associated to id"""
    try:
        return jsonify(UserRepo.fetch_user(user_id=user_id))
    except Exception as e:
        return handle_error(e)

############ RECIPES ###########


@app.post("/users/<user_id>/books/<book_id>/recipes")
def add_recipe(user_id, book_id):
    """Consolidate recipe data. If successful recipes_ingredients record created"""
    try:
        recipe_data = RecipeService.process_recipe_data(
            data={"recipe": request.json}, book_id=book_id, user_id=user_id)
        return jsonify(recipe_data), 200
    except Exception as e:
        return handle_error(e)


@app.get("/users/<user_id>/books/<book_id>/recipes")
def get_book_recipes(user_id, book_id):
    """Return recipes associated to user's book"""
    try:
        recipes = RecipeService.build_recipes(book_id=book_id)
        return jsonify(recipes)
    except Exception as e:
        return handle_error(e)


@app.patch("/users/<user_id>/books/<book_id>/recipes/<recipe_id>")
def update_user_recipe(user_id, book_id, recipe_id):
    """Facilitate editing of recipe and records associated to book"""
    try:
        recipe = RecipeService.process_edit(
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
        book_data = BookService.process_new_book(
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


########### INGREDIENTS ###########


@app.get("/ingredients/<ingredient>")
@jwt_required()
def get_ingredients(ingredient):
    """Facilitates retrieval of ALL options of ingredient components"""
    try:
        ingredients = IngredientService.fetch_ingredients(ingredient)
        return jsonify(ingredients)
    except IntegrityError as e:
        return jsonify({"error": f"get_ingredients error{e}"}), 400


@app.get("/users/<user_id>/ingredients/components")
@check_user_identity
def get_user_ingredients(user_id):
    """Facilitates retrieval of components options associated to User"""
    try:
        return IngredientService.fetch_user_ingredients(user_id=user_id)
    except IntegrityError as e:
        return jsonify({"error": f"get_user_ingredients error{e}"}), 400


@app.get("/users/<user_id>/books/<book_id>/ingredients/components")
@check_user_identity
def get_book_ingredient_components(user_id, book_id):
    """Facilitates retrieval of components options associated to Book"""
    try:
        return IngredientService.fetch_book_ingredient_components(book_id=book_id)
    except IntegrityError as e:
        return jsonify({"error": f"get_book_ingredients error{e}"}), 400


@app.post("/users/<user_id>/books/<book_id>/ingredients/<component>")
@check_user_identity
def add_book_ingredient(user_id, book_id, component):
    """Facilitates creation of book's component option"""
    try:
        return IngredientService.post_ingredient(
            component=component, option=request.json, book_id=book_id)
    except IntegrityError as e:
        return jsonify({"error": f"add_book_ingredient error{e}"}), 400


@app.post("/ingredients/<ingredient>")
# should identity be checked here?
# def add_ingredient(ingredient):
#     """Facilitates creation of ingredient"""
#     value = request.json
#     try:
#         ingredient = IngredientService.add_ingredient(
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
    """Facilitates association of existing instruction to book 
    e.g. adds one book's instructions to another"""
    try:
        InstructionService.create_instruction_association(
            book_id=book_id, instruction_id=instruction_id)
        return jsonify({"message":
                        f"Successful association of instruction{instruction_id} to {book_id}!"})
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
        instructions = InstructionService.fetch_user_instructions(
            user_id=user_id)
        return jsonify(instructions)
    except IntegrityError as e:
        return jsonify({"error": f"/instructions - get_user_instructions error{e}"}), 400


@app.get("/users/<user_id>/books/<book_id>/instructions")
@check_user_identity
def get_book_instructions(user_id, book_id):
    """Facilitates retrieval of book instructions"""
    try:
        has_access = InstructionService.check_book_access(
            user_id=user_id, book_id=book_id)
        if has_access:
            instructions = InstructionService.fetch_book_instructions(
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
