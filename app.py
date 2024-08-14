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
from utils.error_handler import handle_error
# Execute if app doesn't auto update code
# flask --app app.py --debug run

app = Flask(__name__)
load_dotenv()  # This loads the variables from .env into the environment
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # change to False for production
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
    highlight(request,"*")
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


@app.post("/recipes")
def add_recipe():
    """Consolidated recipe data passed to RecipeService function. If successful 
    recipes_ingredients record created"""
    try:
        recipe_data = RecipeService.add_recipe(request.json)

        return jsonify(recipe_data), 200
    except Exception as e:
        return handle_error(e)


@app.post("/books")
def add_book():
    """Facilitates creation of book containing recipes"""
    title = request.json["title"]
    try:    
        book_data = BookRepo.create_book(title)
        return jsonify(book_data), 200
    except IntegrityError as e:
        return jsonify({"error": f"create_book error{e}"}), 400
    

@app.get("/options/<option>")
def get_options(option):
    """Returns options of ingredient components"""

    try:
        options = OptionService.get_options(option)
        return jsonify(options)
    except IntegrityError as e:
        return jsonify({"error": f"get_options error{e}"}), 400



@app.post("/options/<option>")
def add_option(option):
    """Facilitates creation of option for ingredient components"""
    value = request.json[option]

    try:
        OptionService.add_option(option=option, value=value)
    except IntegrityError as e:
        return jsonify({"error": f"add_option error{e}"}), 400

    

################################################################################
def setup_app_context():
    """Function to setup app context. Allows database access via IPython shell"""
    app.app_context().push()
