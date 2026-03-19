import os
from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from repository import *
from models import connect_db, db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request, jwt_required
from exceptions import *
from services.user_services import UserServices
from services.recipes_services import RecipeServices
from services.ingredients_services import IngredientServices
from services.book_services import BookServices
from services.instructions_services import InstructionServices
from decorators.verify_user import verify_jwt_identity
from decorators.handle_route_errors import route_error_handler
from utils.functions import highlight, check_auth_users
from env_config.set_environment import set_environment_config
from env_config.config_cors import configure_cors
from env_config.config_socket import configure_socket
from flask_socketio import emit, disconnect
from services.email_services import EmailServices
from datetime import timedelta
from sqlalchemy import func
import logging
import sys


# Execute if app doesn't auto update code
# flask --app app.py --debug run
# Execute to allow mobile connection
# flask run --host=0.0.0.0

app = Flask(__name__)
set_environment_config(app)
configure_cors(app)
socketio = configure_socket(app)
debug = DebugToolbarExtension(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

connect_db(app)


def enable_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


app_logger = logging.getLogger("app")


@app.route('/__test__')
def test():
    return 'This is working'


# @app.get("/")
# @jwt_required()
# def index():
    # return f"Environment: {app.config['ENV']} - Debug: {app.config['DEBUG']} - Server: {os.environ.get('SERVER_SOFTWARE')}"


@app.post("/signup")
@route_error_handler
def signup():
    """Facilitates new user data, return token"""
    token = UserServices.authenticate_signup(request=request)
    return jsonify({"token": token})


@app.post('/login')
@route_error_handler
def login():
    """Validate user credentials"""
    try:
        token = UserServices.authenticate_login(request=request)
        if not token:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred during login"}), 500


########### USERS ###########
@app.get("/users/<user_id>")
@verify_jwt_identity
@route_error_handler
def get_user(authed_user_id, user_id):
    """Retrieve user associated to id"""
    return jsonify(UserServices.fetch_user(user_id=authed_user_id))


@app.post("/initiate_reset/<email>")
@route_error_handler
def request_reset(email):
    """Verifies User email exists"""
    user = db.session.query(User).filter(
        func.lower(User.email) == email.lower()).first()
    if user:
        reset_token = create_access_token(
            identity=user.id, expires_delta=timedelta(minutes=15))
        EmailServices.create_password_reset_email(
            token=reset_token, recipient_email=user.email)
    return jsonify({"message": "If an account exists, a reset link has been sent."})


@app.post("/request_reset")
@route_error_handler
@jwt_required()
def confirm_reset(authed_user_id):
    """Resets User password"""
    message = UserServices.reset_password(
        user_id=authed_user_id, request=request.json)
    return jsonify(message)


############ RECIPES ###########


@app.post("/users/<user_id>/books/<book_id>/recipes")
@verify_jwt_identity
@route_error_handler
def add_recipe(authed_user_id, book_id, user_id):
    """Consolidate recipe data. If successful recipes_ingredients record created"""
    recipe_data = RecipeServices.process_recipe_data(
        request={"recipe": request.json}, book_id=book_id, user_id=authed_user_id)
    return jsonify(recipe_data), 200


@app.get("/users/<user_id>/books/<book_id>/recipes")
@verify_jwt_identity
@route_error_handler
def get_book_recipes(authed_user_id, book_id, user_id):
    """Return recipes associated to user's book"""
    recipes = RecipeServices.build_recipes(book_id=book_id)
    return jsonify(recipes), 200


@app.patch("/recipes/<recipe_id>")
@verify_jwt_identity
@route_error_handler
def patch_user_recipe(authed_user_id, recipe_id):
    """Facilitate editing of recipe and records associated to book"""
    recipe = RecipeServices.process_edit(user_id=authed_user_id,
                                         data=request.json, recipe_id=recipe_id)
    return jsonify(recipe), 200


@app.delete("/users/<user_id>/books/<book_id>/recipes/<recipe_id>")
@verify_jwt_identity
@route_error_handler
def delete_recipe(authed_user_id, user_id, book_id, recipe_id):
    """Facilitate deletion of recipe record associated to user"""
    response = RecipeServices.remove_recipe(
        auth_id=authed_user_id, recipe_id=recipe_id, data=request.json)
    return jsonify(response), 200

@app.delete("/books/<book_id>/share_recipes/<recipe_id>")
@verify_jwt_identity
@route_error_handler
def delete_shared_recipe(authed_user_id, book_id, recipe_id):
    """Facilitates deletion of association record linking shared recipe to recipient"""
    response = RecipeServices.remove_shared_recipe(authed_id=authed_user_id, recipe_id=recipe_id, book_id=book_id)
    return jsonify(response), 200 


# @app.post("/share_recipes/<recipe_id>")
# @verify_jwt_identity
# @route_error_handler
# def post_share_recipe(recipe_id):
#     """Facilitate user and recipe data to share recipe with recipient"""
#     auth_id = get_jwt_identity()
    # message = RecipeServices.share_recipe(
    #     auth_id=auth_id, recipient=request.json["recipient"], recipe_id=recipe_id)
#     return jsonify(message), 200


########### BOOKS ###########

@app.post("/users/<user_id>/books")
@verify_jwt_identity
@route_error_handler
def add_book(authed_user_id, user_id):
    """Facilitates creation of book"""
    book_data = BookServices.process_new_book(request=request, user_id=authed_user_id)
    return jsonify(book_data), 200


@app.get("/users/<user_id>/books")
@verify_jwt_identity
@route_error_handler
def get_user_books(authed_user_id, user_id):
    """Returns all books associated with user"""
    books = BookServices.fetch_user_books(user_id=authed_user_id)
    return jsonify(books), 200


@app.post("/users/<user_id>/books/<book_id>")
@verify_jwt_identity
@route_error_handler
def add_shared_book(authed_user_id, book_id, user_id):
    """Shares book with User provided in query"""
    recipient = request.json["recipient"]
    response = BookServices.process_shared_book(
        user_id=int(authed_user_id), recipient=recipient, book_id=book_id)
    return jsonify(response), 200

###########  COMPONENT OPTIONS = {amount, unit, item} = INGREDIENT ###########


@app.post("/users/<user_id>/books/<book_id>/ingredients/<component>")
@verify_jwt_identity
@route_error_handler
def add_book_ingredient(authed_user_id, book_id, component, user_id):
    """Facilitates creation of book's component option"""
    return IngredientServices.post_component_option(
        component=component, option=request.json, book_id=book_id)


@app.post("/users/<user_id>/books/<book_id>/components/<component>/options/<option_id>")
@verify_jwt_identity
@route_error_handler
def add_option_association(authed_user_id, book_id, component, option_id, user_id):
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
@verify_jwt_identity
@route_error_handler
def get_user_ingredients(authed_user_id, user_id):
    """Facilitates retrieval of components options associated to User"""
    return IngredientServices.fetch_user_components_options(user_id=authed_user_id)


@app.get("/users/<user_id>/books/<book_id>/ingredients/components")
@verify_jwt_identity
@route_error_handler
def get_book_ingredient_components(authed_user_id, book_id, user_id):
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
@verify_jwt_identity
@route_error_handler
def add_instruction(authed_user_id, book_id, user_id):
    """Facilitates creation of book instruction"""
    instruction = InstructionServices.process_book_instruction(
        request=request.json, book_id=book_id)
    return jsonify(instruction)


@app.post("/users/<user_id>/books/<book_id>/instructions/<instruction_id>")
@verify_jwt_identity
@route_error_handler
def add_instruction_association(authed_user_id, book_id, instruction_id, user_id):
    """Facilitates association of user instruction to book"""
    message = InstructionServices.create_instruction_association(
        book_id=book_id, instruction_id=instruction_id)
    return jsonify(message)


@app.get("/instructions")
@verify_jwt_identity
@route_error_handler
def get_instructions():
    """Facilitates retrieval of instructions"""
    instructions = InstructionRepo.get_instructions()
    return jsonify(instructions)


@app.get("/users/<user_id>/instructions")
@verify_jwt_identity
@route_error_handler
def get_user_instructions(authed_user_id, user_id):
    """Facilitates retrieval of user instructions"""
    instructions = InstructionServices.fetch_user_instructions(
        user_id=authed_user_id)
    return jsonify(instructions)


@app.get("/users/<user_id>/books/<book_id>/instructions")
@verify_jwt_identity
@route_error_handler
def get_book_instructions(authed_user_id, book_id, user_id):
    """Facilitates retrieval of book instructions"""
    response = InstructionServices.fetch_book_instructions(
        book_id=book_id, user_id=authed_user_id)
    return jsonify(response)

################################################################################


# replace with Redis when working with multiple server instances
connected_users = {}
authorized_user = {}


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
                    authorized_user[sid] = identity

        except:
            highlight("Invalid or missing JWT token. Disconnecting.", "#")
            disconnect()
    else:
        highlight("No token provided. Disconnecting.", "#")
        disconnect()


@socketio.on('share_book')
def share_book(data):
    """Facilitates book sharing request and response"""
    user_id = check_auth_users(user_id=authorized_user.get(request.sid))
    
    if not user_id:
        emit('error_sharing_book', {'data': 'Unauthorized'})
        return

    book_id = data.get("currentBookId")
    recipient = data.get("recipient")
    sender = data.get("user")
    title = data.get("currentBook")

    if not all([recipient, book_id, title]):
        emit('error sharing book', {'data': 'Invalid request missing data'})
        return
    
    try:
        response = BookServices.process_shared_book(
            user_id=int(user_id), recipient=recipient, book_id=book_id)
        
        if response["code"] in (422, 409, 404):
            emit('error_sharing_book', {'data': response["message"]})
            return
        
        if response["code"] == 200:
            # SENDER
            sender_id = connected_users.get("user_id")
            emit('book_shared', {
                 "message": response["message"]}, room=sender_id)
            # Handle users that are not connected...
            recipient_id = connected_users.get(response["recipient_id"])
            # RECIPIENT
            if recipient_id:
                message = f"{sender} has shared '{title}' recipe book with you!"
                books = BookServices.fetch_user_books(
                    user_id=response["recipient_id"])
                emit('user_shared_book', {
                     "message": message, "books": books}, room=recipient_id)
                return
            # else:
                # Future logic to que up message for offline recipient       
    except Exception as e:
        emit('error_sharing_book', {'data': 'Something went wrong'})
        app.logger.error(f"socketio - share_book: {e}")
        return
    

@socketio.on('share_recipe')
def share_recipe(data):
    """Facilitates recipe sharing request and response"""
    user_id = check_auth_users(user_id=authorized_user.get(request.sid))
    if not user_id:
        emit('error_sharing_book', {'data': 'Unauthorized'})
        return
    recipe_id = data.get("recipeId")
    sender = data.get("user")
    recipe = data.get("recipeName")
    recipient = data.get("recipient")

    if not all([recipe_id, sender, recipe, recipient]):
            emit('error_sharing_recipe', {'data':'Invalid request missing data'})
            return
    try:
        response = RecipeServices.share_recipe(
            auth_id=user_id, recipient=recipient, recipe_id=recipe_id)
        
        if response["code"] in (400, 403, 404, 409):
            emit('error_sharing_recipe', {'data': response["message"]})
            return

        if response["code"] == 200:
            sender_id = connected_users.get("user_id")
            emit('recipe_shared', {
                 "message": response["message"]}, room=sender_id)
        #Check if recipient is connected
        recipient_id = connected_users.get(response["recipient_id"])
        
        if recipient_id:
            message = f"{sender} has shared '{recipe}'recipe with you!"
            emit('user_shared_recipe', {"message": message, "recipe": response["recipe"]}, room=recipient_id)
            return
        # else:
            # Future logic to que up message for offline recipient
    except Exception as e:
        emit('error_sharing_recipe', {'data': 'Something went wrong'})
        app.logger.error(f"socketio - share_recipe: {e}")
        return


@socketio.on('disconnect')
def disconnected():

    user_sid = request.sid
    user_to_remove = next(
        (k for k, v in connected_users.items() if v == user_sid), None)
    if user_to_remove:
        del connected_users[user_to_remove]
        highlight("user disconnected", "#")


################################################################################
def setup_app_context():
    """Function to setup app context. Allows database access via IPython shell"""
    app.app_context().push()


if __name__ == '__main__':
    socketio.run(app, debug=True)
