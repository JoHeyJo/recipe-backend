import os
from flask import Flask, request, jsonify, current_app
from flask_debugtoolbar import DebugToolbarExtension
from repository import *
from models import connect_db, db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from exceptions import *
from services.user_services import UserServices
from services.recipes_services import RecipeServices
from services.ingredients_services import IngredientServices
from services.book_services import BookServices
from services.instructions_services import InstructionServices
from decorators.verify_user import check_user_identity
from decorators.handle_route_errors import route_error_handler
from utils.functions import highlight
from env_config.set_environment import set_environment
from env_config.config_cors import configure_cors
from env_config.config_socket import configure_socket
from flask_socketio import emit, disconnect
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

# Execute if app doesn't auto update code
# flask --app app.py --debug run
# Execute to allow mobile connection
# flask run --host=0.0.0.0

app = Flask(__name__)
set_environment(app)
configure_cors(app)
socketio = configure_socket(app)
debug = DebugToolbarExtension(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

connect_db(app)


@app.route('/__test__')
def test():
    return 'This is working'


@app.get("/")
# @jwt_required()
def index():
    header = request.headers
    return f"Environment: {app.config['ENV']} - Debug: {app.config['DEBUG']} - Server: {os.environ.get('SERVER_SOFTWARE')}"


# @app.post("/signup")
# @route_error_handler
# def signup():
#     highlight(request,"#")
#     print(request,"signup")
#     """Facilitates new user data, return token"""
#     token = UserServices.authenticate_signup(request=request)
#     return jsonify({"token": token})


@app.post('/login')
@route_error_handler
def login():
    """Validate user credentials"""
    highlight(request, "!")
    print(request, "login")
    try:
        token = UserServices.authenticate_login(request=request)
        if token:
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        current_app.logger.exception("Login error")
        return jsonify({"error": "An error occurred during login"}), 500


########### USERS ###########
@app.get("/users/<user_id>")
@check_user_identity
@route_error_handler
def get_user(user_id):
    """Retrieve user associated to id"""
    return jsonify(UserServices.fetch_user(user_id=user_id))


############ RECIPES ###########


@app.post("/users/<user_id>/books/<book_id>/recipes")
@check_user_identity
@route_error_handler
def add_recipe(user_id, book_id):
    """Consolidate recipe data. If successful recipes_ingredients record created"""
    recipe_data = RecipeServices.process_recipe_data(
        request={"recipe": request.json}, book_id=book_id)
    return jsonify(recipe_data), 200


@app.get("/users/<user_id>/books/<book_id>/recipes")
@check_user_identity
@route_error_handler
def get_book_recipes(user_id, book_id):
    """Return recipes associated to user's book"""
    recipes = RecipeServices.build_recipes(book_id=book_id)
    return jsonify(recipes), 200


@app.patch("/users/<user_id>/books/<book_id>/recipes/<recipe_id>")
@check_user_identity
@route_error_handler
def update_user_recipe(user_id, book_id, recipe_id):
    """Facilitate editing of recipe and records associated to book"""
    recipe = RecipeServices.process_edit(
        data=request.json, recipe_id=recipe_id)
    return jsonify(recipe), 200


@app.delete("/users/<user_id>/books/<book_id>/recipes/<recipe_id>")
@check_user_identity
@route_error_handler
def get_delete_recipe(user_id, book_id, recipe_id):
    """Facilitate deletion of recipe record associated to user"""
    response = RecipeServices.remove_recipe(recipe_id=recipe_id)
    return jsonify(response), 200


########### BOOKS ###########

@app.post("/users/<user_id>/books")
@check_user_identity
@route_error_handler
def add_book(user_id):
    """Facilitates creation of book"""
    book_data = BookServices.process_new_book(request=request, user_id=user_id)
    return jsonify(book_data), 200


@app.get("/users/<user_id>/books")
@check_user_identity
@route_error_handler
def get_user_books(user_id):
    """Returns all books associated with user"""
    books = BookServices.fetch_user_books(user_id=user_id)
    return jsonify(books), 200


@app.post("/users/<user_id>/books/<book_id>")
@check_user_identity
@route_error_handler
def add_shared_book(user_id, book_id):
    """Shares book with User provided in query"""
    recipient = request.json["recipient"]
    response = BookServices.process_shared_book(
        user_id=int(user_id), recipient=recipient, book_id=book_id)
    return jsonify(response), 200

###########  COMPONENT OPTIONS = {amount, unit, item} = INGREDIENT ###########


@app.post("/users/<user_id>/books/<book_id>/ingredients/<component>")
@check_user_identity
@route_error_handler
def add_book_ingredient(user_id, book_id, component):
    """Facilitates creation of book's component option"""
    return IngredientServices.post_component_option(
        component=component, option=request.json, book_id=book_id)


@app.post("/users/<user_id>/books/<book_id>/components/<component>/options/<option_id>")
@check_user_identity
@route_error_handler
def add_option_association(user_id, book_id, component, option_id):
    """Facilitates association of user option to book"""
    response = IngredientServices.create_option_association(
        component=component, book_id=book_id, option_id=option_id)
    return jsonify(response)


# @app.get("/ingredients/<ingredient>")
# @jwt_required()
# @route_error_handler
# def get_ingredients(ingredient):
#     """Facilitates retrieval of ALL options of ingredient components"""
#     ingredients = IngredientServices.fetch_components_options(ingredient)
#     return jsonify(ingredients)


@app.get("/users/<user_id>/ingredients/components")
@check_user_identity
@route_error_handler
def get_user_ingredients(user_id):
    """Facilitates retrieval of components options associated to User"""
    return IngredientServices.fetch_user_components_options(user_id=user_id)


@app.get("/users/<user_id>/books/<book_id>/ingredients/components")
@check_user_identity
@route_error_handler
def get_book_ingredient_components(user_id, book_id):
    """Facilitates retrieval of components options associated to Book"""
    return IngredientServices.fetch_book_components_options(book_id=book_id)


@app.post("/ingredients/<ingredient>")
# should identity be checked here?
# def add_ingredient(ingredient):
#     """Facilitates creation of ingredient"""
#     value = request.json
#     try:
#         ingredient = IngredientServices.add_ingredient(
#             option=ingredient, value=value)
#         return jsonify(ingredient)
#     except IntegrityError as e:
#         return jsonify({"error": f"add_ingredient error{e}"}), 400
########### INSTRUCTIONS ###########
@app.post("/users/<user_id>/books/<book_id>/instructions")
@check_user_identity
@route_error_handler
def add_instruction(user_id, book_id):
    """Facilitates creation of book instruction"""
    instruction = InstructionServices.process_book_instruction(
        request=request.json, book_id=book_id)
    return jsonify(instruction)


@app.post("/users/<user_id>/books/<book_id>/instructions/<instruction_id>")
@check_user_identity
@route_error_handler
def add_instruction_association(user_id, book_id, instruction_id):
    """Facilitates association of user instruction to book"""
    message = InstructionServices.create_instruction_association(
        book_id=book_id, instruction_id=instruction_id)
    return jsonify(message)


@app.get("/instructions")
@check_user_identity
@route_error_handler
def get_instructions():
    """Facilitates retrieval of instructions"""
    instructions = InstructionRepo.get_instructions()
    return jsonify(instructions)


@app.get("/users/<user_id>/instructions")
@check_user_identity
@route_error_handler
def get_user_instructions(user_id):
    """Facilitates retrieval of user instructions"""
    instructions = InstructionServices.fetch_user_instructions(
        user_id=user_id)
    return jsonify(instructions)


@app.get("/users/<user_id>/books/<book_id>/instructions")
@check_user_identity
@route_error_handler
def get_book_instructions(user_id, book_id):
    """Facilitates retrieval of book instructions"""
    response = InstructionServices.fetch_book_instructions(
        book_id=book_id, user_id=user_id)
    return jsonify(response)

################################################################################


connected_users = {}


@socketio.on('connect')
def handle_connect(auth):
    """Establish WebSocket connection"""
    token = auth["token"]
    user_id = auth["userId"]
    sid = request.sid
    if token:
        try:
            with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
                verify_jwt_in_request()
                identity = get_jwt_identity()
                if identity == user_id:
                    connected_users[user_id] = sid

        except:
            highlight("Invalid or missing JWT token. Disconnecting.", "#")
            disconnect()
    else:
        highlight("No token provided. Disconnecting.", "#")
        disconnect()


@socketio.on('share')
def share_book(data):
    """Facilitate share book request and response"""
    user_id = data["userId"]
    book_id = data["currentBookId"]
    recipient = data["recipient"]
    sender = data["user"]
    title = data["currentBook"]
    try:
        response = BookServices.process_shared_book(
            user_id=int(user_id), recipient=recipient, book_id=book_id)
        if response["code"] == 200:
            # SENDER
            emit('book_shared', response["message"], room=user_id)
            connection_id = connected_users[response["recipient_id"]]
            # RECIPIENT
            if connection_id:
                message = f"{sender} has shared '{title}' recipe book with you!"
                books = BookServices.fetch_user_books(
                    user_id=response["recipient_id"])
                emit('user_shared_book', {
                     "message": message, "books": books}, room=connection_id)
            # else:
                # Future logic to que up message for offline recipient
        if response["code"] == 422 or 409 or 404:
            emit('error_sharing_book', {'data': response["message"]})
    except Exception as e:
        raise e


@socketio.on('disconnect')
def disconnected():
    user_sid = request.sid
    for key, value in connected_users.items():
        if user_sid == value:
            del connected_users[key]
            highlight("user disconnected", "#")
            return


################################################################################
if __name__ == '__main__':
    socketio.run(app, debug=True)


def setup_app_context():
    """Function to setup app context. Allows database access via IPython shell"""
    app.app_context().push()
