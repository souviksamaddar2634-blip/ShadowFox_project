from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, Optional

from database import get_db
from schemas.user import UserCreate
from utils.security import get_password_hash
from utils.exceptions import DuplicateEmailException, DuplicateUsernameException, DatabaseOperationError
from utils.logger import logger

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user from MongoDB by their ObjectId or raw string ID (fallback)."""
    db = get_db()
    try:
        if ObjectId.is_valid(user_id):
            doc = db.users.find_one({"_id": ObjectId(user_id)})
            if doc:
                return doc
        # Fallback to direct string lookup (e.g. for mock IDs or custom IDs)
        return db.users.find_one({"_id": user_id})
    except Exception as e:
        logger.error(f"Error finding user by ID '{user_id}': {e}")
        raise DatabaseOperationError(str(e))

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user from MongoDB by their username."""
    db = get_db()
    try:
        return db.users.find_one({"username": username.strip()})
    except Exception as e:
        logger.error(f"Error finding user by username '{username}': {e}")
        raise DatabaseOperationError(str(e))

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user from MongoDB by their email address (lowercase normalized)."""
    db = get_db()
    try:
        return db.users.find_one({"email": email.strip().lower()})
    except Exception as e:
        logger.error(f"Error finding user by email '{email}': {e}")
        raise DatabaseOperationError(str(e))

def create_user(payload: UserCreate) -> Dict[str, Any]:
    """Validate, normalize, hash password, and insert a new user document into MongoDB."""
    db = get_db()
    
    username = payload.username.strip()
    email = payload.email.strip().lower()
    
    logger.info(f"Database write: Starting signup process for username '{username}' (email: '{email}')")
    
    # Validate username uniqueness
    if get_user_by_username(username) is not None:
        logger.warning(f"Signup event failure: Username '{username}' already exists.")
        raise DuplicateUsernameException()
        
    # Validate email uniqueness
    if get_user_by_email(email) is not None:
        logger.warning(f"Signup event failure: Email '{email}' is already registered.")
        raise DuplicateEmailException()
        
    try:
        # Hash password securely using bcrypt context
        hashed_password = get_password_hash(payload.password)
        
        new_user = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "favorite_player": payload.favorite_player,
            "createdAt": datetime.utcnow(),
            "role": "user" # default role
        }
        
        result = db.users.insert_one(new_user)
        new_user["_id"] = result.inserted_id
        
        logger.info(f"Signup event success: User '{username}' registered with ID '{result.inserted_id}'.")
        return new_user
    except Exception as e:
        logger.error(f"Error executing user insert in MongoDB: {e}")
        raise DatabaseOperationError(str(e))
