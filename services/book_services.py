from repository import BookRepo, UserBookRepo
from models import db, User
from repository import UserRepo
from models import UserBook, BookRole


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
    def process_shared_book(recipient, book_id):
        """Calls services for book processing"""
        try:
            stmt = db.select(User).where(User.user_name == recipient)
            user = db.session.execute(stmt).scalar_one_or_none()
            recipient_id = user.id
            user = UserRepo.query_user(user_id=recipient_id)
            if user:
                relation_exists = db.session.get(
                    UserBook, (book_id, recipient_id))
                if relation_exists:
                    return {"message": "User already has access to this book!"}
                else:
                    UserBookRepo.create_entry(
                        user_id=recipient_id, book_id=book_id, role=BookRole.collaborator)
                    return {"message": f"Book shared with {user.user_name}!"}
            else:
                return {"message": "User not found"}
        except Exception as e:
            raise
