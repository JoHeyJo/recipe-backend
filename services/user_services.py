from repository import db, UserRepo, Book, User
from utils.functions import highlight
import time
from flask import current_app


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
        highlight(request, "HIT authenticate_login")
        t0 = time.time()
        highlight(request, f"HIT authenticate_login t0={t0}")
        current_app.logger.warning("authenticate_login: start t=%.3f", t0)
        current_app.logger.warning(
            "authenticate_login: about to read request.json")
        t1 = time.time()
        user_name = request.json["userName"]
        password = request.json["password"]
        t2 = time.time()
        current_app.logger.warning(
            "authenticate_login: finished reading JSON in %.3f seconds",
            t2 - t1,
        )
        current_app.logger.warning(
            "authenticate_login: about to call UserRepo.login")
        t3 = time.time()
        token = UserRepo.login(user_name=user_name, password=password)
        t4 = time.time()
        current_app.logger.warning(
            "authenticate_login: UserRepo.login returned in %.3f seconds",
            t4 - t3,
        )
        current_app.logger.warning(
            "authenticate_login: total time %.3f seconds", t4 - t0
        )
        try:
            token = UserRepo.login(user_name=user_name, password=password)
            highlight(token, "HIT token")
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
