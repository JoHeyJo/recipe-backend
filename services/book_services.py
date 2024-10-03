from repository import BookRepo, UserBookRepo, highlight
from models import db, User

class BookService():
    """Handles book view business logic"""
    @staticmethod
    def process_new_book(book_data, user_id):
        """Call repo to create book. Associate book to user - set default if none """
        new_book = BookRepo.create_book(title=book_data["title"], description=book_data["description"])
        # associate book to user
        if new_book["id"]:
            UserBookRepo.create_entry(user_id=user_id, book_id=new_book["id"])
        # add book id to default if necessary
        user = User.query.get(user_id)
        if user.book_id == None:
            user.book_id = new_book["id"]
            db.session.add(user)
            db.session.commit()
        return new_book
        

