from repository import BookRepo, UserBookRepo
from models import db, User
from repository import UserRepo
from models import UserBook, BookRole, BookType
from utils.functions import highlight
from services.user_services import UserServices


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
                user_book = UserBookRepo.create_entry(
                    user_id=user_id, book_id=new_book["id"])
                new_book["book_role"] = user_book.role.value

            # add book id to default if necessary
            UserServices.assign_default_book_if_none_set(
                user_id=user_id, book_id=new_book["id"])

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
    def process_shared_book(user_id, recipient_name, book_id):
        """Calls services for book processing"""
        try:
            recipient = UserRepo.query_user_name(user_name=recipient_name)

            if not recipient:
                return {"message": "User not found", "error": "Not Found", "code": 404}

            if (recipient.id == user_id):
                return {"message": "Don't you already have this book???",
                        "error": "Unprocessable Content", "code": 422
                        }

            response = BookServices.share_book(recipient=recipient, shared_book_id=book_id,
                                               recipient_has_default_book=recipient.default_book_id)
            return response
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def share_book(recipient, shared_book_id, recipient_has_default_book):
        """"Creates association with recipient. Sets book as default if recipient has none"""
        try:
            if recipient_has_default_book:
                recipient_has_shared_book = UserBookRepo.query_user_book(
                    book_id=shared_book_id, user_id=recipient.id)

                if recipient_has_shared_book:
                    return {"message": "User already has access to this book!",
                            "error": "Unprocessable Content", "code": 409
                            }

            user_book = UserBookRepo.create_entry(
                user_id=recipient.id, book_id=shared_book_id, role=BookRole.collaborator)

            book = BookRepo.build_book(user_book=user_book)

            if recipient_has_default_book is None:
                recipient.default_book_id = book["id"]

            db.session.commit()
            return {"recipient_id": recipient.id,
                    "message": f"Book shared with {recipient.user_name}!",
                    "code": 200,
                    "payload": book
                    }
        except Exception as e:
            raise type(e)(f"BookServices - share_book error :{e}") from e
