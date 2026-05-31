import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

from utils.exceptions import raise_unauthorized_access, raise_token_expired
from utils.logger import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Configure OAuth2 bearer scheme for JWT token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token containing claims and an expiration timestamp."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Placeholder for future refresh token architecture.
    Returns a long-lived JWT token to request new access tokens.
    """
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "scope": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Decode a JWT access token and verify its integrity and expiration."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            logger.error("Token verification failure: subject (sub) claim missing in JWT.")
            raise_unauthorized_access("Token is missing user identification claim.")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failure: JWT token has expired.")
        raise_token_expired()
    except JWTError as e:
        logger.error(f"Token verification failure: JWT decode failed: {e}")
        raise_unauthorized_access("Invalid authentication token signature.")

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """FastAPI dependency to extract the current authenticated user from a Bearer token."""
    if not token:
        logger.warning("Authentication failure: Authorization Bearer header is missing.")
        raise_unauthorized_access("Not authenticated. Please provide a bearer token.")
    
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    # Import user_service locally to prevent circular package imports
    from services import user_service
    user = user_service.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Authentication failure: User ID '{user_id}' does not exist in database.")
        raise_unauthorized_access("User associated with this token no longer exists.")
        
    return user

def check_role(required_role: str):
    """FastAPI dependency factory for verifying specific user roles (e.g. admin checks)."""
    def role_dependency(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if current_user.get("role") != required_role:
            logger.warning(
                f"Authorization failure: User '{current_user.get('username')}' (role: {current_user.get('role')}) "
                f"denied access to resource requiring role '{required_role}'."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permissions: {required_role} role."
            )
        return current_user
    return role_dependency
