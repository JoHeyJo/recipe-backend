from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db
from repository import UserRepo
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SECRET_KEY'] = "oh-so-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sling_it'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

debug = DebugToolbarExtension(app)

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
    except IntegrityError as e:
       return jsonify({"error": f"Error in signup: {e}"})
