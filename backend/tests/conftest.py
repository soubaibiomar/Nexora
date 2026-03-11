"""
Shared pytest fixtures for the Nexora test suite.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app


@pytest.fixture(scope="session")
def client():
    """Reusable TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_token(client):
    """Register a test user and return a valid JWT token."""
    # Use the default admin credentials to get a token
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Return Authorization headers with a valid Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}
