from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserResponse


class GoogleTokenRequest(BaseModel):
    google_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None