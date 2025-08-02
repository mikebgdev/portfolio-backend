import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.models.user import User


class TestAuthAPI:
    """Integration tests for authentication API endpoints."""

    @patch('app.auth.oauth.auth_service.verify_google_token')
    def test_login_success_new_user(self, mock_verify_google, client, db):
        """Test successful login with new user creation."""
        # Mock Google token verification
        mock_verify_google.return_value = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'sub': '123456789'
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json={"google_token": "valid_google_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New User"
        
        # Verify user was created in database
        user = db.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None

    @patch('app.auth.oauth.auth_service.verify_google_token')
    def test_login_success_existing_user(self, mock_verify_google, client, test_user):
        """Test successful login with existing user."""
        mock_verify_google.return_value = {
            'email': test_user.email,
            'name': test_user.name,
            'sub': '123456789'
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json={"google_token": "valid_google_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user"]["email"] == test_user.email
        assert data["user"]["id"] == test_user.id

    @patch('app.auth.oauth.auth_service.verify_google_token')
    def test_login_invalid_google_token(self, mock_verify_google, client):
        """Test login with invalid Google token."""
        mock_verify_google.side_effect = Exception("Invalid token")
        
        response = client.post(
            "/api/v1/auth/login",
            json={"google_token": "invalid_token"}
        )
        
        assert response.status_code == 400
        assert "Token verification failed" in response.json()["detail"]

    @patch('app.auth.oauth.auth_service.verify_google_token')
    def test_login_missing_email(self, mock_verify_google, client):
        """Test login when Google token doesn't contain email."""
        mock_verify_google.return_value = {
            'name': 'User Without Email',
            'sub': '123456789'
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json={"google_token": "token_without_email"}
        )
        
        assert response.status_code == 400
        assert "Email not found" in response.json()["detail"]

    def test_get_current_user_info(self, authenticated_client, test_user):
        """Test getting current user information."""
        response = authenticated_client.get("/api/v1/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["role"] == test_user.role

    def test_get_current_user_info_unauthorized(self, client):
        """Test getting user info without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No token provided

    def test_get_current_user_info_invalid_token(self, client):
        """Test getting user info with invalid token."""
        client.headers.update({"Authorization": "Bearer invalid_token"})
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    def test_auth_status(self, authenticated_client, test_user):
        """Test authentication status endpoint."""
        response = authenticated_client.get("/api/v1/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["authenticated"] is True
        assert data["user_id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role

    def test_auth_status_unauthorized(self, client):
        """Test auth status without authentication."""
        response = client.get("/api/v1/auth/status")
        
        assert response.status_code == 403