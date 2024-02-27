from flask_jwt_extended import create_access_token
# from flask_bcrypt import Bcrypt


# bcrypt = Bcrypt()

# class Repo():
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
