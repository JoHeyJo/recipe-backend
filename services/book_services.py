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
    def process_shared_book(user_id, recipient, book_id):
        """Calls services for book processing"""
        try:
            recipient = UserRepo.query_user_name(user_name=recipient)

            if not recipient:
                return {"message": "User not found", "error": "Not Found", "code": 404}
             
            if (recipient.id == user_id):
                return {"message": "Don't you already have this book???",
                        "error": "Unprocessable Content", "code": 422
                        }
            
            relation_exists = UserBookRepo.query_shared_book(book_id=book_id, user_id=recipient.id)

            if relation_exists:
                return {"message": "User already has access to this book!",
                        "error": "Unprocessable Content", "code": 409
                        }
            if not relation_exists:
                book = UserBookRepo.create_entry(
                    user_id=recipient.id, book_id=book_id, role=BookRole.collaborator)
                
                is_default_assigned = UserServices.assign_default_book_if_none_set(user_id=recipient.id, book_id=book_id)
                if is_default_assigned:
                    book_with_role = BookRepo.build_book(
                        user_id=recipient.id, book_id=book.book_id)
                    
                    db.session.commit()
                    return {"recipient_id": recipient.id,
                            "message": f"Book shared with {recipient.user_name}!",
                            "code": 200,
                            "payload":book_with_role
                            }
                db.session.commit()
                return {"recipient_id": recipient.id,
                        "message": f"Book shared with {recipient.user_name}!",
                        "code": 200
                        }
                
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def share_book_no_default_book():
        """User shares Book with Recipient that has no default book assigned"""

    @staticmethod
    def share_book_has_default_book():
        """User shares with Recipient that has assigned default book"""
