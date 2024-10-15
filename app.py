from models import User
import os
from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from repository import *
from models import connect_db, db
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flask_cors import CORS
from exceptions import *
from services.recipes_services import RecipeService
from services.options_services import OptionService
from services.book_services import BookService
from utils.error_handler import handle_error
# Execute if app doesn't auto update code
# flask --app app.py --debug run

app = Flask(__name__)
load_dotenv()  # This loads the variables from .env into the environment
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # change to False for production
app.config['DEBUG'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # does this auto update flask app?

debug = DebugToolbarExtension(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)

connect_db(app)
# CORS(app, resources={r"/*": {"origins": "*"}})

CORS(app)  # SPECIFY CORS OPTIONS FOR RESOURCES FOR DEPLOYMENT ^^^^^


@app.get("/")
def index():
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
def get_user(user_id):
    """Retrieve user associated to id"""
    try:
        return jsonify(UserRepo.fetch_user(user_id=user_id))
    except Exception as e:
        return handle_error(e)

############ RECIPES ###########


@app.post("/users/<user_id>/books/<book_id>/recipes")
def add_recipe(user_id, book_id):
    """Consolidated recipe data passed to RecipeService function. If successful 
    recipes_ingredients record created"""
    try:
        recipe_data = RecipeService.process_recipe_data(
            data={"recipe": request.json}, book_id=book_id, user_id=user_id)
        return jsonify(recipe_data), 200
    except Exception as e:
        return handle_error(e)


@app.get("/users/<user_id>/books/<book_id>/recipes")
def get_user_recipes(user_id, book_id):
    """Return recipes associated to user"""
    try:
        # recipes = RecipeRepo.fetch_recipes(user_id=user_id,book_id=book_id)
        recipes = RecipeService.build_recipes(book_id=book_id)
        return jsonify(recipes)
        # return jsonify(recipes)
    except Exception as e:
        return handle_error(e)



########### BOOKS ###########


@app.post("/books/users/<user_id>")
def add_book(user_id):
    """Facilitates creation of book containing recipes"""
    title = request.json["title"]
    description = request.json["description"]
    book_data = {"title": title, "description": description}
    try:
        book_data = BookService.process_new_book(
            book_data=book_data, user_id=user_id)
        return jsonify(book_data), 200
    except IntegrityError as e:
        return jsonify({"error": f"create_book error{e}"}), 400


@app.get("/books/users/<user_id>")
def get_user_books(user_id):
    """Returns all books associated with user"""
    books = BookRepo.get_user_books(user_id=user_id)
    return jsonify({"books": books})

########### OPTIONS ###########


@app.get("/options/<option>")
def get_options(option):
    """Facilitates retrieval of options of ingredient components"""
    try:
        options = OptionService.get_options(option)
        return jsonify(options)
    except IntegrityError as e:
        return jsonify({"error": f"get_options error{e}"}), 400


@app.post("/options/<option>")
def add_option(option):
    """Facilitates creation of option for ingredient components"""
    value = request.json
    try:
        option = OptionService.add_option(label=option, attributes=value)
        return jsonify(option)
    except IntegrityError as e:
        return jsonify({"error": f"add_option error{e}"}), 400

########### INSTRUCTIONS ###########


@app.post("/instructions/instruction")
def add_instruction():
    """Facilitates creation of instruction"""
    instruction = request.json["instruction"]
    try:
        instruction = InstructionRepo.create_instruction(
            instruction=instruction)
        return jsonify(instruction)
    except IntegrityError as e:
        return jsonify({"error": f"add_instruction error{e}"}), 400


@app.get("/instructions")
def get_instructions():
    """Facilitates retrieval of instructions """
    try:
        instructions = InstructionRepo.get_instructions()
        return jsonify(instructions)
    except IntegrityError as e:
        return jsonify({"error": f"/instructions - get_instructions error{e}"}), 400


################################################################################
def setup_app_context():
    """Function to setup app context. Allows database access via IPython shell"""
    app.app_context().push()
