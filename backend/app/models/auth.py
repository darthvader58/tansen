"""Authentication data models."""
from pydantic import BaseModel
from datetime import datetime


class GoogleAuthRequest(BaseModel):
    """Google OAuth authentication request."""
    id_token: str


class AuthResponse(BaseModel):
    """Authentication response."""
    user_id: str
    session_token: str
    expires_at: datetime
    user: dict


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    email: str
    exp: datetime
    iat: datetime
