import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    favorite_player: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        # Username: alphanumeric and underscores only, length 3-20
        username_clean = v.strip()
        if not (3 <= len(username_clean) <= 20):
            raise ValueError("Username must be between 3 and 20 characters in length.")
        if not re.match(r"^[a-zA-Z0-9_]+$", username_clean):
            raise ValueError("Username must only contain letters, numbers, and underscores.")
        return username_clean

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        # Normalize to lowercase and validate basic syntax
        email_clean = v.strip().lower()
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_clean):
            raise ValueError("Invalid email format.")
        return email_clean

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Password: minimum length 8, 1 uppercase, 1 lowercase, 1 number
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one numerical digit.")
        return v

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    favorite_player: str
    role: str
    createdAt: datetime
