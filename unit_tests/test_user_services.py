import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from services.user_services import UserServices
from repository import UserRepo, highlight

# ✅ Test: User Exists


@patch("repository.UserRepo.query_user")
def test_fetch_user_success(mock_query_user):
    """Test fetch_user returns serialized user when found."""
    mock_query_user.return_value = MagicMock(
        id=1, user_name="testuser", default_book_id=2
    )

    # Mock serialization
    with patch("models.User.serialize") as mock_serialize:
        mock_serialize.return_value = {
            "id": 1, "user_name": "testuser", "default_book_id": 2}

        user = UserServices.fetch_user(user_id=1)
        assert user == {"id": 1, "user_name": "testuser", "default_book_id": 2}
        mock_query_user.assert_called_once_with(user_id=1)

# ❌ Test: User Not Found


@patch("repository.UserRepo.query_user")
def test_fetch_user_not_found(mock_query_user):
    """Test fetch_user raises ValueError when user is not found."""
    mock_query_user.return_value = None  # Simulate missing user

    with pytest.raises(ValueError, match="User not found"):
        UserServices.fetch_user(user_id=99)  # User ID that doesn't exist

# ❌ Test: Database Error


@patch("repository.UserRepo.query_user")
def test_fetch_user_database_error(mock_query_user):
    """Test fetch_user raises SQLAlchemyError when DB fails."""
    mock_query_user.side_effect = SQLAlchemyError(
        "Database failure")  # Simulate DB error

    with pytest.raises(SQLAlchemyError):
        UserServices.fetch_user(user_id=1)
