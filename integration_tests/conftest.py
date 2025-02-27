import pytest
from app import app, db
from models import User  # Import your models
import os

@pytest.fixture(scope="module")
def test_client():
    """Set up a Flask test client with PostgreSQL as the test DB."""

    # Configure the app to use the PostgreSQL test database
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "TEST_DATABASE_URL", "postgresql://postgres:password@localhost/sling_it_test"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "test_secret_key"

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()  # Create tables in the test database
            yield testing_client  # Provide the client to tests
            db.session.remove()
            db.drop_all()  # Clean up after tests
