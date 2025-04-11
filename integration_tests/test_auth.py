import pytest
from flask_jwt_extended import decode_token
from app import db
from models import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# ✅ Helper Function: Add Test User to Database


def create_test_user():
    """Insert a test user into the database."""
    hashed_pwd = bcrypt.generate_password_hash("validpassword").decode("utf-8")
    user = User(first_name="test",
                last_name="user",
                user_name="testuser",
                email="test@example.com", 
                password=hashed_pwd)
    db.session.add(user)
    db.session.commit()

# ✅ Test Successful Login


def test_login_success(test_client):
    """Test valid login returns a token (200)."""
    create_test_user()  # Add a test user to DB

    response = test_client.post(
        "/login", json={"userName": "testuser", "password": "validpassword"})
    assert response.status_code == 200
    assert "token" in response.json

    decoded_token = decode_token(response.json["token"])
    assert decoded_token["sub"] == 1  # Ensure user ID is correct

# ❌ Test Invalid Password


def test_login_invalid_password(test_client):
    """Test login with incorrect password (401)."""
    response = test_client.post(
        "/login", json={"userName": "testuser", "password": "wrongpassword"})

    assert response.status_code == 401
    assert response.json == {"error": "Invalid credentials"}

# ❌ Test Non-Existent User


def test_login_non_existent_user(test_client):
    """Test login with a non-existent user (401)."""
    response = test_client.post(
        "/login", json={"userName": "nouser", "password": "password"})

    assert response.status_code == 401
    assert response.json == {"error": "Invalid credentials"}

# ❌ Test Database Error Handling


def test_login_database_error(test_client, monkeypatch):
    """Test login handling a database error (500)."""

    def mock_login_error(*args, **kwargs):
        raise Exception("Database connection failed")


    monkeypatch.setattr("repository.UserRepo.login", mock_login_error)

    response = test_client.post(
        "/login", json={"userName": "testuser", "password": "validpassword"})

    assert response.status_code == 500
    assert response.json == {"error": "An error occurred during login"}
