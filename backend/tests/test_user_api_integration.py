"""
Integration tests for User API endpoints with mocked Firebase authentication
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any
import json
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import auth
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

# Mock environment variables before importing the app
@pytest.fixture(autouse=True)
def mock_environment():
    """Mock required environment variables"""
    with patch.dict(os.environ, {
        "FIREBASE_PROJECT_ID": "test-project",
        "DATABASE_URL": "sqlite:///test.db",
        "ALLOWED_ORIGINS": "*",
        "ALLOWED_HOSTS": "*"
    }):
        yield

@pytest.fixture
def client():
    """Create test client with mocked dependencies"""
    # Import after environment is mocked
    from backend.main import app

    with patch('backend.api.middleware.auth.initialize_firebase'):
        with patch('backend.config.firebase.validate_firebase_environment') as mock_validate:
            mock_validate.return_value = {"valid": True, "project_id": "test-project"}
            return TestClient(app)

@pytest.fixture
def sample_decoded_token() -> Dict[str, Any]:
    """Sample decoded Firebase token"""
    return {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/avatar.jpg",
        "email_verified": True,
        "firebase": {"identities": {"email": ["test@example.com"]}},
        "custom_claims": {}
    }

class TestUserAPIIntegration:
    """Integration tests for User API endpoints"""

    def test_health_endpoint(self, client):
        """Test basic health check endpoint"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "corner-league-api"
        assert data["version"] == "1.0.0"

    def test_firebase_health_endpoint(self, client):
        """Test Firebase health check endpoint"""
        with patch('backend.api.middleware.auth.check_firebase_health') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "firebase_initialized": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            response = client.get("/health/firebase")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"

    def test_config_health_endpoint(self, client):
        """Test configuration health check endpoint"""
        response = client.get("/health/config")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True

    def test_me_endpoint_without_token(self, client):
        """Test /me endpoint without authentication token"""
        response = client.get("/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_users_me_endpoint_without_token(self, client):
        """Test /users/me endpoint without authentication token"""
        response = client.get("/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_api_v1_users_me_endpoint_without_token(self, client):
        """Test /api/v1/users/me endpoint without authentication token"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_api_v1_me_preferences_endpoint_without_token(self, client):
        """Test /api/v1/me/preferences endpoint without authentication token"""
        response = client.get("/api/v1/me/preferences")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_me_preferences_endpoint_without_token(self, client):
        """Test /me/preferences endpoint without authentication token"""
        response = client.get("/me/preferences")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_auth_firebase_endpoint_without_token(self, client):
        """Test /auth/firebase endpoint without authentication token"""
        response = client.get("/auth/firebase")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_invalid_token_handling(self, client):
        """Test handling of invalid Firebase tokens"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")

            response = client.get(
                "/me",
                headers={"Authorization": "Bearer invalid_token"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "INVALID_TOKEN"

    def test_expired_token_handling(self, client):
        """Test handling of expired Firebase tokens"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired", Exception("test cause"))

            # Use a properly formatted JWT-like token to pass initial validation
            long_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature-that-is-long-enough-to-pass-validation-checks"

            response = client.get(
                "/me",
                headers={"Authorization": f"Bearer {long_token}"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "EXPIRED_TOKEN"

    def test_malformed_token_handling(self, client):
        """Test handling of malformed tokens"""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid.token.format"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "MALFORMED_TOKEN"

    def test_empty_token_handling(self, client):
        """Test handling of empty tokens"""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer "}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "EMPTY_TOKEN"

    def test_short_token_handling(self, client):
        """Test handling of tokens that are too short"""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer abc"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "MALFORMED_TOKEN"

    def test_public_sports_endpoint_without_auth(self, client):
        """Test /public/sports endpoint without authentication"""
        with patch('backend.api.services.user_service.get_current_user_context') as mock_context:
            mock_context.return_value = None

            response = client.get("/public/sports")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_preferences"] is False
            assert "sports" in data

    def test_me_endpoint_with_valid_token_but_no_user(self, client, sample_decoded_token):
        """Test /me endpoint with valid token but user doesn't exist in database"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock user context that creates new user
            mock_user_context = Mock()
            mock_user_context.get_user_profile.return_value = None

            # Mock database user creation
            mock_db_user = Mock()
            mock_db_user.id = "test_user_123"
            mock_db_user.firebase_uid = "test_user_123"
            mock_db_user.email = "test@example.com"
            mock_db_user.display_name = "Test User"
            mock_db_user.is_onboarded = False
            mock_db_user.created_at = datetime.now(timezone.utc)
            mock_db_user.updated_at = datetime.now(timezone.utc)
            mock_db_user.last_active_at = datetime.now(timezone.utc)

            mock_user_context.get_or_create_db_user.return_value = mock_db_user
            mock_context.return_value = mock_user_context

            # Use a properly formatted JWT-like token
            long_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature-that-is-long-enough-to-pass-validation-checks"

            response = client.get(
                "/me",
                headers={"Authorization": f"Bearer {long_token}"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["firebase_uid"] == "test_user_123"
            assert data["email"] == "test@example.com"

    def test_connection_error_handling(self, client):
        """Test handling of Firebase connection errors"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = ConnectionError("Firebase unreachable")

            long_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature-that-is-long-enough-to-pass-validation-checks"

            response = client.get(
                "/me",
                headers={"Authorization": f"Bearer {long_token}"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "SERVICE_UNAVAILABLE"

    def test_preferences_endpoint_validation(self, client, sample_decoded_token):
        """Test preferences endpoint with valid authentication"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user:

            mock_verify.return_value = sample_decoded_token

            # Mock database user
            mock_user = Mock()
            mock_user.sport_preferences = []
            mock_user.team_preferences = []
            mock_user.notification_settings = None
            mock_db_user.return_value = mock_user

            long_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature-that-is-long-enough-to-pass-validation-checks"

            response = client.get(
                "/me/preferences",
                headers={"Authorization": f"Bearer {long_token}"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "sport_preferences" in data
            assert "team_preferences" in data
            assert "notification_settings" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])