from repository import BookRepo, UserBookRepo, highlight

class BookService():
    """Handles book view business logic"""
    @staticmethod
    def process_new_book(book_data, user_id):
        """Call repo to create book. If successful associate book to user"""
        new_book = BookRepo.create_book(title=book_data["title"], description=book_data["description"])
        if new_book["id"]:
            UserBookRepo.create_entry(user_id=user_id, book_id=new_book["id"])
            return new_book