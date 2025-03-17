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
