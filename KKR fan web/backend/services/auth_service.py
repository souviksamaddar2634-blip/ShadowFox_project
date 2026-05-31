import time
from typing import Any, Dict

from schemas.auth import UserLogin
from services import user_service
from utils.security import verify_password
from utils.auth import create_access_token
from utils.exceptions import InvalidCredentialsException
from utils.logger import logger

def authenticate_user(payload: UserLogin) -> Dict[str, Any]:
    """
    Authenticate user login credentials.
    Supports login via both username or email, and records authentication response times.
    """
    username_or_email = payload.username.strip()
    start_time = time.time()
    
    logger.info(f"Auth event: Processing login attempt for identifier '{username_or_email}'")
    
    # 1. Fetch user by username, fallback to email
    user = user_service.get_user_by_username(username_or_email)
    if not user:
        user = user_service.get_user_by_email(username_or_email)
        
    # 2. Check user exists
    if not user:
        response_time_ms = (time.time() - start_time) * 1000
        logger.warning(
            f"Login failure: Identifier '{username_or_email}' not found. "
            f"Auth duration: {response_time_ms:.2f}ms."
        )
        raise InvalidCredentialsException()
        
    # 3. Verify password
    password_hash = user.get("hashed_password", "")
    is_valid = verify_password(payload.password, password_hash)
    response_time_ms = (time.time() - start_time) * 1000
    
    if not is_valid:
        logger.warning(
            f"Login failure: Incorrect password for user '{user.get('username')}'. "
            f"Auth duration: {response_time_ms:.2f}ms."
        )
        raise InvalidCredentialsException()
        
    logger.info(
        f"Login success: User '{user.get('username')}' authenticated. "
        f"Auth duration: {response_time_ms:.2f}ms."
    )
    
    # 4. Generate JWT access token with MongoDB ID (as string) in 'sub' claim
    user_id_str = str(user["_id"])
    token_claims = {
        "sub": user_id_str,
        "username": user.get("username"),
        "role": user.get("role")
    }
    
    access_token = create_access_token(data=token_claims)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
