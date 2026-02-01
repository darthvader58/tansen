"""
Test security and authentication.
"""
import pytest
from datetime import datetime, timedelta, timezone
import jwt

from app.core.security import create_access_token, decode_access_token
from app.core.exceptions import AuthenticationError
from app.config import settings


@pytest.mark.unit
def test_create_access_token():
    """Test JWT token creation."""
    user_id = "test-user-123"
    email = "test@example.com"
    
    token = create_access_token(user_id, email)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.unit
def test_decode_access_token():
    """Test JWT token decoding."""
    user_id = "test-user-123"
    email = "test@example.com"
    
    token = create_access_token(user_id, email)
    payload = decode_access_token(token)
    
    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert "exp" in payload
    assert "iat" in payload


@pytest.mark.unit
def test_decode_expired_token():
    """Test decoding expired token raises error."""
    # Create token that expires immediately
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "test-user",
        "email": "test@example.com",
        "exp": now - timedelta(seconds=1),
        "iat": now,
    }
    
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    with pytest.raises(AuthenticationError) as exc_info:
        decode_access_token(token)
    
    assert "expired" in str(exc_info.value).lower()


@pytest.mark.unit
def test_decode_invalid_token():
    """Test decoding invalid token raises error."""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(AuthenticationError):
        decode_access_token(invalid_token)
