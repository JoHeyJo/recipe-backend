from models import User
import os
from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from repository import UserRepo, RecipeRepo, QuantityAmountRepo, QuantityUnitRepo, RecipeIngredientRepo
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
    
@app.post("/add")
def add_recipe():
    """Consolidates recipe data before calling repo functions. If successful RecipeIngredients record created"""
    name = request.json["name"]
    preparation = request.json["preparation"]
    notes = request.json["notes"]
    unit = request.json["unit"]
    quantity = request.json["quantity"]


    try:
        recipe_id = RecipeRepo.addRecipe(name, preparation, notes)
        quantity_unit_id = QuantityUnitRepo.addQuantityUnit(unit=unit)
        quantity_amount_id = QuantityAmountRepo.addQuantityAmount(amount=quantity)

        # try:
        #     RecipeIngredientRepo.createRecipe(
        #         recipe_id=recipe_id,
                
        #     )
        
        # return jsonify(recipe)
    except IntegrityError as e:
        return jsonify({"error": f"add_ingredient error: {e}"}), 400
