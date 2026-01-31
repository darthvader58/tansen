"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.config import settings
from app.core.exceptions import AuthenticationError, ErrorCode

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


def create_access_token(user_id: str, email: str) -> str:
    """
    Create JWT access token.
    
    Args:
        user_id: User ID
        email: User email
        
    Returns:
        JWT token string
    """
    expiration = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)
    
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User information from token
        
    Raises:
        AuthenticationError: If authentication fails
    """
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
        return {
            "user_id": payload["sub"],
            "email": payload["email"],
        }
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Dependency to get current user if authenticated, None otherwise.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User information or None
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        return {
            "user_id": payload["sub"],
            "email": payload["email"],
        }
    except AuthenticationError:
        return None
