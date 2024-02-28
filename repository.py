from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from models import User, db
from sqlalchemy.exc import IntegrityError

bcrypt = Bcrypt()

class UserRepo():
    @staticmethod
    def signup(user_name, first_name, last_name, email, password):
        """Sign up user. Hashes password and adds user to system."""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
        )

        token = create_access_token(identity=user.user_name)

        try:
          db.session.add(user)
          db.session.commit()
          return token
        except IntegrityError as e:
           db.session.rollback()
           return {"error":f"error in UserRepo.signup =>{e}"}


