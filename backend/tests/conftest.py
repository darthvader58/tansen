"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
import os

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ["FIREBASE_STORAGE_BUCKET"] = "test-bucket"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "display_name": "Test User",
    }


@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers with test token."""
    from app.core.security import create_access_token
    
    token = create_access_token(
        user_id=test_user["user_id"],
        email=test_user["email"],
    )
    
    return {
        "Authorization": f"Bearer {token}"
    }
