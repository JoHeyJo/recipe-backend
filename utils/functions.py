from sqlalchemy.dialects.postgresql import insert

def insert_first(Model, data, column_name, db):
    """Insert-first data entry method leveraging SQLAlchemy CORE. Auto commits session"""
    try:
        # Insert with conflict handling
        stmt = (
            insert(Model)
            .values(**{column_name: data})
            .on_conflict_do_nothing()
            .returning(Model.id, getattr(Model, column_name))
        )

        # Execute the insert and fetch result - this is NOT a separate query.
        result = db.session.execute(stmt).fetchone()

        # If no result (conflict occurred), query the existing record
        if result is None:
            quantity_amount = db.session.query(
                Model).filter_by(**{column_name: data}).one()
        else:
            # Map result to Model instance
            quantity_amount = Model(id=result.id, **{column_name: result[1]})

        return quantity_amount

    except Exception as e:
        raise type(e)(f"insert_first: Database error occurred: {e}") from e


def highlight(value, divider):
    print(divider * 10)
    print(value)
    print(divider * 10)

# Future implementation - Template of helper functions for role modification of UserBook table

# from sqlalchemy import select, update, delete
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import Session
# from models.user_book import User, Book, UserBookMembership
# from models.roles import BookRole

# def grant_collaborator(session: Session, book_id: int, user_id: int):
#     # Upsert-ish: insert or update role to collaborator
#     m = session.get(UserBookMembership, {"user_id": user_id, "book_id": book_id})
#     if m is None:
#         m = UserBookMembership(user_id=user_id, book_id=book_id, role=BookRole.collaborator)
#         session.add(m)
#     else:
#         m.role = BookRole.collaborator

# def revoke_access(session: Session, book_id: int, user_id: int):
#     # Owners cannot be revoked here; handle separately
#     q = delete(UserBookMembership).where(
#         UserBookMembership.user_id == user_id,
#         UserBookMembership.book_id == book_id,
#         UserBookMembership.role != BookRole.owner
#     )
#     session.execute(q)

# def transfer_ownership(session: Session, book_id: int, from_user_id: int, to_user_id: int):
#     """
#     Do it in a transaction. The partial unique index ('one owner per book')
#     will protect us against race conditions.
#     """
#     # demote current owner to collaborator
#     session.execute(
#         update(UserBookMembership)
#         .where(
#             UserBookMembership.book_id == book_id,
#             UserBookMembership.user_id == from_user_id,
#             UserBookMembership.role == BookRole.owner
#         )
#         .values(role=BookRole.collaborator)
#     )
#     # promote new owner
#     m = session.get(UserBookMembership, {"user_id": to_user_id, "book_id": book_id})
#     if m is None:
#         m = UserBookMembership(user_id=to_user_id, book_id=book_id, role=BookRole.owner)
#         session.add(m)
#     else:
#         m.role = BookRole.owner

#     # OPTIONAL: keep Book.created_by in sync
#     b = session.get(Book, book_id)
#     b.created_by = to_user_id

#     try:
#         session.flush()  # triggers the partial unique index
#     except IntegrityError:
#         session.rollback()
#         raise RuntimeError("Transfer failed: owner already exists for this book.")

# def books_visible_to(session: Session, user_id: int):
#     stmt = (
#         select(Book)
#         .join(UserBookMembership, UserBookMembership.book_id == Book.id)
#         .where(UserBookMembership.user_id == user_id)
#     )
#     return session.execute(stmt).scalars().all()

