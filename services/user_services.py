from repository import db, UserRepo
from sqlalchemy.exc import SQLAlchemyError


class UserServices():
    """Handles ingredients view business logic"""


@staticmethod
def authenticate(request):
    """Process user credentials"""
    user_name = request.json["userName"]
    first_name = request.json["firstName"]
    last_name = request.json["lastName"]
    password = request.json["password"]
    email = request.json["email"]
    try:
        token = UserRepo.signup(user_name, first_name,
                                last_name, email, password)
        return token
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
