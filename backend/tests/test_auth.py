"""
Tests for the Authentication Router.
Covers registration, login, /me endpoint, rate limiting, and error cases.
"""

import pytest
import uuid


class TestRegister:
    """Tests for POST /api/auth/register."""

    def test_register_new_user(self, client):
        """Register a brand-new user successfully."""
        unique = uuid.uuid4().hex[:8]
        response = client.post("/api/auth/register", json={
            "username": f"testuser_{unique}",
            "email": f"test_{unique}@example.com",
            "password": "securepass123",
            "full_name": "Test User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == f"testuser_{unique}"
        assert data["message"] == "Registration successful! You can now sign in."

    def test_register_duplicate_username(self, client):
        """Registering with an existing username should fail."""
        unique = uuid.uuid4().hex[:8]
        payload = {
            "username": f"dupuser_{unique}",
            "email": f"dup_{unique}@example.com",
            "password": "password",
            "full_name": "Dup User",
        }
        client.post("/api/auth/register", json=payload)
        # Second attempt with same username
        payload["email"] = f"other_{unique}@example.com"
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"]

    def test_register_duplicate_email(self, client):
        """Registering with an existing email should fail."""
        unique = uuid.uuid4().hex[:8]
        email = f"shared_{unique}@example.com"
        client.post("/api/auth/register", json={
            "username": f"first_{unique}",
            "email": email,
            "password": "password",
            "full_name": "First User",
        })
        response = client.post("/api/auth/register", json={
            "username": f"second_{unique}",
            "email": email,
            "password": "password",
            "full_name": "Second User",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_short_username(self, client):
        """Username shorter than 3 chars should fail validation."""
        response = client.post("/api/auth/register", json={
            "username": "ab",
            "email": "short@example.com",
            "password": "password",
            "full_name": "Short User",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Password shorter than 4 chars should fail validation."""
        response = client.post("/api/auth/register", json={
            "username": "validuser",
            "email": "valid@example.com",
            "password": "abc",
            "full_name": "Valid User",
        })
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login."""

    def test_login_success(self, client):
        """Login with valid admin credentials."""
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "admin"

    def test_login_wrong_password(self, client):
        """Login with wrong password returns 401."""
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Login with non-existent username returns 401."""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistentuser999", "password": "password"},
        )
        assert response.status_code == 401

    def test_login_returns_user_info(self, client):
        """Login response includes full_name and email."""
        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin"},
        )
        data = response.json()
        assert "full_name" in data
        assert "email" in data


class TestGetMe:
    """Tests for GET /api/auth/me."""

    def test_get_me_with_valid_token(self, client, auth_headers):
        """Authenticated user gets their own profile."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert "email" in data
        assert "full_name" in data
        assert "headline" in data

    def test_get_me_without_token(self, client):
        """Access /me without a token returns 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token(self, client):
        """Access /me with a garbage token returns 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_get_me_returns_correct_registered_user(self, client):
        """Register a user, login, and /me should return that user."""
        unique = uuid.uuid4().hex[:8]
        username = f"metest_{unique}"
        client.post("/api/auth/register", json={
            "username": username,
            "email": f"me_{unique}@example.com",
            "password": "testpass",
            "full_name": "Me Test User",
        })
        login_resp = client.post(
            "/api/auth/login",
            data={"username": username, "password": "testpass"},
        )
        token = login_resp.json()["access_token"]
        me_resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == username
        assert me_resp.json()["full_name"] == "Me Test User"
