from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db

app = Flask(__name__)

app.config['SECRET_KEY'] = "oh-so-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sling_it'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.app_context().push()
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.get("/")
def index():
  return "hello"

