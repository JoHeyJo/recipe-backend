from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import User, db, Ingredient
from sqlalchemy.exc import IntegrityError
from exceptions import *

bcrypt = Bcrypt()

class UserRepo():
    """Facilitate User table interactions"""
    @staticmethod
    def signup(user_name, first_name, last_name, email, password):
        """Sign up user. Hashes password and adds user to system. => Token"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
            is_admin=False
        )
        token = create_access_token(identity=user.user_name)
        try:
          db.session.add(user)
          db.session.commit()
          return token
        except IntegrityError as e:
            db.session.rollback()
            if "users_user_name_key" in str(e.orig):
                raise UsernameAlreadyTakenError(
                    "This username is already taken.")
            elif "users_email_key" in str(e.orig):
                raise EmailAlreadyRegisteredError(
                    "This email is already taken.")
            else:
                raise SignUpError("An error occurred during signup.")
            
    @staticmethod
    def authenticate(user_name, password):
        """Find user with username and password. Return False for incorrect credentials"""

        user = User.query.filter_by(user_name=user_name).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                token = create_access_token(
                    identity=user.user_name, additional_claims={"is_admin": user.is_admin})
                return token
        return False  


class IngredientRepo():
    """Facilitates Ingredient table interactions"""
    @staticmethod
    def addIngredient(name, preparation, notes):
        """Add ingredient"""
        ingredient = Ingredient(name=name, preparation=preparation, notes=notes)
        try:
            db.session.add(ingredient)
            db.session.commit()
            return {"message":"Ingredient added"}
        except IntegrityError as e:
            db.session.rollback()
            return 


    

