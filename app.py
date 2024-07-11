from models import User
import os
from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from repository import UserRepo, RecipeRepo, QuantityAmountRepo, QuantityUnitRepo, RecipeIngredientRepo, IngredientsRepo, highlight, BookRepo
from models import connect_db, db
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flask_cors import CORS
from exceptions import *
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
    """Create new user, add to DB, return token"""

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


@app.post("/add_recipe")
def add_recipe():
    """Consolidates recipe data before calling repo functions. If successful 
    recipes_ingredients record created"""
    # User data
    user_id = request.json["user_id"]

    # Recipe data
    recipe = request.json["recipe"]
    recipe_name = recipe["name"]
    preparation = recipe["preparation"] or None
    notes = recipe["notes"] or None

    # Ingredient data
    ingredients = recipe["ingredients"] or None
    # First add ingredients if applicable then add recipe
    try:
        if ingredients: 
            ingredients_data = IngredientsRepo.add_ingredients(ingredients)

            recipe_data = RecipeRepo.add_recipe(
                name=recipe_name, preparation=preparation, notes=notes)

            recipe_data['ingredients'] = ingredients_data

            for ingredient in recipe_data['ingredients']:
                RecipeIngredientRepo.create_recipe(
                    recipe_id=recipe_data['recipe_id'], 
                    ingredient_id=ingredient['ingredient_id'],
                    quantity_amount_id=ingredient['amount_id'], 
                    quantity_unit_id=ingredient['unit_id'])

            return jsonify(recipe_data), 200
        else:
            recipe_data = RecipeRepo.add_recipe(
                name=recipe_name, preparation=preparation, notes=notes)
            highlight("added just recipe name",'*')
            return jsonify(recipe_data), 200

    except IntegrityError as e:
        return jsonify({"error": f"add_ingredient error - calling RecipeRepo & ingredients Repo: {e}"}), 400


@app.post("/add_book")
def add_book():
    """Facilitates creation of book containing recipes"""
    title = request.json["title"]
    try:    
        book_data = BookRepo.add_book(title)
        return jsonify(book_data), 200
    except IntegrityError as e:
        return jsonify({"error": f"add_book error{e}"}), 400


