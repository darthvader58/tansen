"""
Test health check endpoint.
"""
import pytest


@pytest.mark.unit
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


@pytest.mark.unit
def test_health_check_returns_correct_structure(client):
    """Test health check returns expected structure."""
    response = client.get("/health")
    data = response.json()
    
    required_fields = ["status", "version", "environment"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
