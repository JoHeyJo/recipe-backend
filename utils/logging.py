import logging
import traceback
from sqlalchemy import event

def log_tracback():
# Enable INFO-level logging for SQLAlchemy
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)

    @event.listens_for(db.session, "after_rollback")
    def receive_after_rollback(session):
        print("⚠️ SQLAlchemy session rollback triggered!")
        print("Rollback stack trace:")
        traceback.print_stack()

    @event.listens_for(db.engine, "rollback")
    def receive_engine_rollback(conn):
        print("⚠️ Engine rollback triggered!")
        print("Rollback stack trace:")
        traceback.print_stack()
