from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT
from sqlalchemy.orm import DeclarativeBase ,Mapped, mapped_column
from annotations import str_255
from mixins import TableNameMixin, TimestampMixin
from flask_jwt_extended import create_access_token
# from flask_bcrypt import Bcrypt


# bcrypt = Bcrypt()
db = SQLAlchemy()


# Creating a base class
class Base(DeclarativeBase):
  pass


class User(Base, TableNameMixin, TimestampMixin):
    """Users table"""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str_255]
    last_name: Mapped[str_255]
    email: Mapped[str_255]
    password: Mapped[str_255]
    user_name: Mapped[str_255]

    # @classmethod
    # def signup(cls, username, first_name, last_name, email, password, image_url):
    #     """Sign up user.

    #     Hashes password and adds user to system.
    #     """

    #     hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

    #     user = User(
    #         username=username,
    #         first_name=first_name,
    #         last_name=last_name,
    #         email=email,
    #         password=hashed_pwd,
    #         image_url=image_url,
    #     )

    #     token = create_access_token(identity=username)

    #     db.session.add(user)
    #     return token

    # @classmethod
    # def authenticate(cls, username, password):
    #     """Find user with `username` and `password`.

    #     It searches for a user whose password hash matches this password
    #     and, if it finds such a user, returns that user object.

    #     If can't find matching user (or if password is wrong), returns False.
    #     """

    #     user = cls.query.filter_by(username=username).first()

    #     if user:
    #         try:
    #             is_auth = bcrypt.check_password_hash(user.password, password)
    #             if is_auth:
    #                 token = create_access_token(identity=username)
    #                 return token
    #         except LookupError:
    #             return 
    #     return False

    # def serialize(self):
    #     """Serialize to dictionary."""

    #     return {
    #         "username":self.username,
    #         "firstName":self.first_name,
    #         "lastName":self.last_name,
    #         "email":self.email,
    #         "imageUrl":self.image_url,
    #     }


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
