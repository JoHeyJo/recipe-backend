from repository import BookRepo, UserBookRepo
from models import db, User

class BookServices():
    """Handles book view business logic"""
    @staticmethod
    def process_new_book(request, user_id):
        """Call repo to create book. Associate book to user - set default if none """
        title = request.json["title"]
        description = request.json["description"]
        book_data = {"title": title, "description": description}
        try:
            new_book = BookRepo.create_book(title=book_data["title"], description=book_data["description"])
            # associate book to user
            if new_book["id"]:
                UserBookRepo.create_entry(user_id=user_id, book_id=new_book["id"])
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
        

