from repository import db, UserRepo, Book, User
from utils.functions import highlight
from datetime import timedelta
from flask_jwt_extended import create_access_token


class UserServices():
    """Handles ingredients view business logic"""
    @staticmethod
    def authenticate_signup(request):
        """Process new user information"""
        user_name = request.json["userName"]
        first_name = request.json["firstName"]
        last_name = request.json["lastName"]
        password = request.json["password"]
        email = request.json["email"]
        try:
            token = UserRepo.signup(user_name, first_name,
                                    last_name, email, password)
            db.session.commit()
            return token
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def authenticate_login(request):
        """Process user credentials - read-only operation"""
        user_name = request.json["userName"]
        password = request.json["password"]
        try:
            token = UserRepo.login(user_name=user_name, password=password)
            return token
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def fetch_user(user_id):
        """Retrieve user - inject default book object"""
        try:
            user = UserRepo.query_user(user_id=user_id)
            if not user:
                raise ValueError("User not found")
            user_data = User.serialize(user)

            default_book_id = user_data.get("default_book_id")

            if default_book_id:
                default_book = Book.serialize(Book.query.get(default_book_id))
                user_data["default_book"] = default_book
            return user_data
        except Exception:
            raise

    @staticmethod
    def generate_password_reset_token(user_id):
        """Generates specialized time sensitive token"""
        expires = timedelta(minutes=30)
        reset_token = create_access_token(
        identity=user_id, expires_delta=expires, additional_claims={"type": "password_reset"})
        return reset_token

    @staticmethod
    def reset_password(user_id, password):
        """Replaces current User password with new password"""
        try:
            user = UserRepo.query_user(user_id=user_id)
            user.password = password
            db.session.commit()
        except Exception:
            db.session.rollback()
        raise
        
