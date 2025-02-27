from repository import db, UserRepo
from sqlalchemy.exc import SQLAlchemyError


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
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def authenticate_login(request):
        """Process user credentials - read-only operation"""
        user_name = request.json["userName"]
        password = request.json["password"]
        try:
            token = UserRepo.login(user_name=user_name, password=password)
            return token
        except SQLAlchemyError as e:
            raise e
