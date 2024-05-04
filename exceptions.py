class UsernameAlreadyTakenError(Exception):
    """Exception raised when the username is already taken."""
    pass


class EmailAlreadyRegisteredError(Exception):
    """Exception raised when the email is already registered."""
    pass


class InvalidEmailError(Exception):
    """Exception raised for invalid email formats."""
    pass


class WeakPasswordError(Exception):
    """Exception raised for passwords that are too weak."""
    pass

class InvalidCredentials(Exception):
    """Exception raised for invalid credentials"""
    pass

class SignUpError(Exception):
    """Exception raised during sign up"""
    pass