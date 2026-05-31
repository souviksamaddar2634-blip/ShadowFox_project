from fastapi import HTTPException, status

class KKRBackendException(Exception):
    """Base exception for KKR Fan Web Backend"""
    pass

class DatabaseConnectionError(KKRBackendException):
    """Raised when connection to MongoDB fails"""
    pass

class DatabaseOperationError(KKRBackendException):
    """Raised when an operation (insert, update, query) on MongoDB fails"""
    pass

class InvalidCredentialsException(KKRBackendException):
    """Raised on invalid username/email or password credentials"""
    pass

class DuplicateEmailException(KKRBackendException):
    """Raised when signup email already exists in collection"""
    pass

class DuplicateUsernameException(KKRBackendException):
    """Raised when signup username already exists in collection"""
    pass

class UnauthorizedAccessException(KKRBackendException):
    """Raised when access is unauthorized or has missing header scopes"""
    pass

class InvalidTokenException(KKRBackendException):
    """Raised when the JWT signature or payload is invalid"""
    pass

class ExpiredTokenException(KKRBackendException):
    """Raised when the JWT validation fails due to token expiration"""
    pass

# Centralized HTTP Exception raising helpers
def raise_invalid_credentials():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials. Please check your username/email and password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_duplicate_email():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="A user with this email is already registered."
    )

def raise_duplicate_username():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This username is already taken."
    )

def raise_unauthorized_access(details: str = "Not authenticated"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=details,
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_token_expired():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication token has expired. Please sign in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_db_connection_error(details: str):
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Database connection unavailable: {details}"
    )

def raise_db_operation_error(details: str):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database operation failed: {details}"
    )

def raise_bad_request_error(details: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=details
    )
