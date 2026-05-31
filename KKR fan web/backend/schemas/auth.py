from pydantic import BaseModel
from schemas.user import UserResponse

class UserLogin(BaseModel):
    username: str  # Can accept username or email address
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
