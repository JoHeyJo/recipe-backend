import pytest
from unittest.mock import patch, MagicMock
from app import app
from services import user_services
from repository import UserRepo


@pytest.fixture
def client():
    """Fixture to create a test client for Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ✅ Test Successful Login


@patch("repository.UserRepo.login")  # Mocking database call
def test_login_success(mock_login, client):
    """Test valid login returns a token (200)."""
    mock_login.return_value = "mock_token_123"  # Simulate valid token

    response = client.post(
        "/login", json={"userName": "testuser", "password": "validpassword"})

    assert response.status_code == 200
    assert "token" in response.json
    assert response.json["token"] == "mock_token_123"

# ❌ Test Invalid Password


@patch("repository.UserRepo.login")
def test_login_invalid_password(mock_login, client):
    """Test login with incorrect password (401)."""
    mock_login.return_value = False  # Simulate failed authentication

    response = client.post(
        "/login", json={"userName": "testuser", "password": "wrongpassword"})

    assert response.status_code == 401
    assert response.json == {"error": "Invalid credentials"}

# ❌ Test Non-Existent User


@patch("repository.UserRepo.login")
def test_login_non_existent_user(mock_login, client):
    """Test login with a non-existent user (401)."""
    mock_login.return_value = False  # User not found

    response = client.post(
        "/login", json={"userName": "nouser", "password": "password"})

    assert response.status_code == 401
    assert response.json == {"error": "Invalid credentials"}

# ❌ Test Database Error Handling


@patch("repository.UserRepo.login")
def test_login_database_error(mock_login, client):
    """Test login handling a database error (500)."""
    mock_login.side_effect = Exception(
        "Database error!")  # Simulate DB failure

    response = client.post(
        "/login", json={"userName": "testuser", "password": "password"})

    assert response.status_code == 500
    assert response.json == {"error": "An error occurred during login"}
