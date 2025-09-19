from repository import BookRepo, UserBookRepo
from models import db, User
from repository import UserRepo
from models import UserBook, BookRole
from utils.functions import highlight


class BookServices():
    """Handles book view business logic"""
    @staticmethod
    def process_new_book(request, user_id):
        """Call repo to create book. Associate book to user - set default if none """
        title = request.json["title"]
        description = request.json["description"]
        book_data = {"title": title, "description": description}
        try:
            new_book = BookRepo.create_book(
                title=book_data["title"], description=book_data["description"])
            # associate book to user
            if new_book["id"]:
                UserBookRepo.create_entry(
                    user_id=user_id, book_id=new_book["id"])
            # add book id to default if necessary
            user = User.query.get(user_id)
            if user.default_book_id == None:
                user.default_book_id = new_book["id"]
                db.session.add(user)
            db.session.commit()
            return new_book
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def fetch_user_books(user_id):
        """Calls repo function to query user's books"""
        try:
            return BookRepo.query_user_books(user_id=user_id)
        except Exception as e:
            raise

    @staticmethod
    def process_shared_book(user_id, recipient, book_id):
        """Calls services for book processing"""
        try:
            stmt = db.select(User).where(User.user_name == recipient)
            recipient = db.session.execute(stmt).scalar_one_or_none()
            if recipient:
                if (recipient.id == user_id):
                    return {"message": "Don't you already have this book???",
                            "error": "Unprocessable Content", "code": 422
                            }

                relation_exists = db.session.get(
                    UserBook, (book_id, recipient.id))

                if relation_exists:
                    return {"message": "User already has access to this book!",
                            "error": "Unprocessable Content", "code": 409
                            }
                else:
                    UserBookRepo.create_entry(
                        user_id=recipient.id, book_id=book_id, role=BookRole.collaborator)
                    db.session.commit()
                    return {"recipient_id": recipient.id,
                            "message": f"Book shared with {recipient.user_name}!",
                            "error": "Unprocessable Content", "code": 200
                            }
            else:
                return {"message": "User not found", "error": "Not Found", "code": 404}
        except Exception as e:
            db.session.rollback()
            raise
