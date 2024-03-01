from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from repository import UserRepo
from models import connect_db, db
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
# from flask_migrate import Migrate 

app = Flask(__name__)

app.config['SECRET_KEY'] = "oh-so-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sling_it'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # change to False for production
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # does this auto update flask app?

debug = DebugToolbarExtension(app)
jwt = JWTManager(app)

# migrate = Migrate(app, db)

# from models import User

connect_db(app)

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
       token = UserRepo.signup(user_name, first_name, last_name, password, email)
       return jsonify({"token": token})
    except BaseException as e:
       return jsonify({"error": f"Sign up error: {e}"}), 400
    

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
       return jsonify({"error": f"login error: {e}"}), 401
    
