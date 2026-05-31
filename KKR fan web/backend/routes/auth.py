from fastapi import APIRouter, Depends, status
from typing import Dict, Any

from schemas.auth import UserLogin, TokenResponse
from schemas.user import UserCreate, UserResponse
from services import auth_service, user_service
from utils.auth import get_current_user, create_access_token
from utils.serializer import serialize_doc
from utils.exceptions import (
    DuplicateUsernameException,
    DuplicateEmailException,
    InvalidCredentialsException,
    raise_duplicate_username,
    raise_duplicate_email,
    raise_invalid_credentials
)

router = APIRouter()

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate):
    """Register a new user, automatically generate access tokens, and login."""
    try:
        user = user_service.create_user(payload)
    except DuplicateUsernameException:
        raise_duplicate_username()
    except DuplicateEmailException:
        raise_duplicate_email()
        
    # Generate token immediately for auto-login after registration
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
        "user": serialize_doc(user)
    }

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin):
    """Verify login credentials and return an access token."""
    try:
        result = auth_service.authenticate_user(payload)
        # Serialize nested user document
        result["user"] = serialize_doc(result["user"])
        return result
    except InvalidCredentialsException:
        raise_invalid_credentials()

@router.get("/me", response_model=UserResponse)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieve details of the currently authenticated user."""
    return serialize_doc(current_user)

@router.get("/verify")
def verify(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verify validity of a token and return current user details."""
    return {
        "status": "valid",
        "user": serialize_doc(current_user)
    }
