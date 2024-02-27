from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db

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

