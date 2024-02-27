from flask import Flask,  request, python

app = Flask(__name__)

app.config['SECRET_KEY'] = "oh-so-secret"
debug = DebugToolbarExtension(app)

@app.get("/")
def home():
  """home page"""
  