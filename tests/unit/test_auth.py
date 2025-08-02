import pytest
from unittest.mock import patch, MagicMock
from jose import jwt
from datetime import datetime, timedelta

from app.auth.oauth import auth_service
from app.config import settings


class TestAuthService:
    """Test cases for AuthService class."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        test_data = {"sub": "test@example.com", "user_id": 1}
        token = auth_service.create_access_token(test_data)
        
        # Verify token is created
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token can be decoded
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_custom_expiry(self):
        """Test JWT token creation with custom expiration."""
        test_data = {"sub": "test@example.com"}
        custom_delta = timedelta(minutes=60)
        token = auth_service.create_access_token(test_data, custom_delta)
        
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        
        # Check that expiration is roughly 60 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + custom_delta
        time_diff = abs((exp_time - expected_time).total_seconds())
        assert time_diff < 5  # Allow 5 second tolerance

    def test_verify_token_valid(self):
        """Test verification of valid JWT token."""
        test_data = {"sub": "test@example.com", "user_id": 1}
        token = auth_service.create_access_token(test_data)
        
        payload = auth_service.verify_token(token)
        
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1

    def test_verify_token_invalid(self):
        """Test verification of invalid JWT token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception) as exc_info:
            auth_service.verify_token(invalid_token)
        
        assert exc_info.value.status_code == 401

    def test_verify_token_expired(self):
        """Test verification of expired JWT token."""
        test_data = {"sub": "test@example.com"}
        # Create token that expires immediately
        expired_delta = timedelta(seconds=-1)
        token = auth_service.create_access_token(test_data, expired_delta)
        
        with pytest.raises(Exception) as exc_info:
            auth_service.verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_verify_google_token_valid(self, mock_verify):
        """Test Google token verification with valid token."""
        mock_verify.return_value = {
            'aud': settings.google_client_id,
            'email': 'test@example.com',
            'name': 'Test User',
            'sub': '123456789'
        }
        
        result = auth_service.verify_google_token("valid_google_token")
        
        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'
        mock_verify.assert_called_once()

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_verify_google_token_invalid(self, mock_verify):
        """Test Google token verification with invalid token."""
        mock_verify.side_effect = ValueError("Invalid token")
        
        with pytest.raises(Exception) as exc_info:
            auth_service.verify_google_token("invalid_google_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid Google token" in str(exc_info.value.detail)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_verify_google_token_wrong_audience(self, mock_verify):
        """Test Google token verification with wrong audience."""
        mock_verify.return_value = {
            'aud': 'wrong-client-id',
            'email': 'test@example.com'
        }
        
        with pytest.raises(Exception) as exc_info:
            auth_service.verify_google_token("token_with_wrong_audience")
        
        assert exc_info.value.status_code == 401