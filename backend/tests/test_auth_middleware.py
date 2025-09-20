"""
Tests for Firebase JWT authentication middleware
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

import firebase_admin
from firebase_admin import auth
from fastapi import FastAPI, Depends, status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from backend.api.middleware.auth import (
    FirebaseJWTMiddleware,
    FirebaseAuthRequired,
    AuthError,
    initialize_firebase,
    firebase_auth_required,
    firebase_auth_optional
)
from backend.api.schemas.auth import FirebaseUser
from backend.api.exceptions import register_exception_handlers


# Test application for middleware testing
test_app = FastAPI()
register_exception_handlers(test_app)


@test_app.get("/protected")
async def protected_endpoint(user: FirebaseUser = Depends(firebase_auth_required)):
    return {"user_id": user.uid, "email": user.email}


@test_app.get("/optional")
async def optional_endpoint(user: FirebaseUser = Depends(firebase_auth_optional)):
    if user:
        return {"authenticated": True, "user_id": user.uid}
    return {"authenticated": False}


@test_app.get("/public")
async def public_endpoint():
    return {"message": "public endpoint"}


class TestFirebaseJWTMiddleware:
    """Test Firebase JWT middleware functionality"""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance for testing"""
        return FirebaseJWTMiddleware()

    @pytest.fixture
    def mock_firebase_app(self):
        """Mock Firebase app initialization"""
        with patch('backend.api.middleware.auth._firebase_app') as mock_app:
            yield mock_app

    @pytest.fixture
    def sample_decoded_token(self) -> Dict[str, Any]:
        """Sample decoded Firebase token"""
        return {
            "uid": "test_user_123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg",
            "email_verified": True,
            "firebase": {
                "identities": {
                    "email": ["test@example.com"]
                }
            },
            "custom_claims": {"role": "user"}
        }

    @pytest.mark.asyncio
    async def test_valid_token_validation(self, middleware, sample_decoded_token):
        """Test validation of valid Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.return_value = sample_decoded_token

            result = await middleware.validate_token("valid_token")

            assert result.is_valid
            assert result.firebase_user is not None
            assert result.firebase_user.uid == "test_user_123"
            assert result.firebase_user.email == "test@example.com"
            assert result.firebase_user.email_verified is True
            mock_verify.assert_called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_invalid_token_validation(self, middleware):
        """Test validation of invalid Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")

            result = await middleware.validate_token("invalid_token")

            assert not result.is_valid
            assert result.error_code == "INVALID_TOKEN"
            assert "invalid" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_expired_token_validation(self, middleware):
        """Test validation of expired Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired", Exception("test cause"))

            result = await middleware.validate_token("expired_token")

            assert not result.is_valid
            assert result.error_code == "EXPIRED_TOKEN"
            assert "expired" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_revoked_token_validation(self, middleware):
        """Test validation of revoked Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.RevokedIdTokenError("Token revoked")

            result = await middleware.validate_token("revoked_token")

            assert not result.is_valid
            assert result.error_code == "REVOKED_TOKEN"
            assert "revoked" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_missing_token_validation(self, middleware):
        """Test validation with missing token"""
        result = await middleware.validate_token("")

        assert not result.is_valid
        assert result.error_code == "MISSING_TOKEN"

    @pytest.mark.asyncio
    async def test_certificate_fetch_error(self, middleware):
        """Test handling of certificate fetch errors"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.CertificateFetchError("Certificate error", Exception("test cause"))

            result = await middleware.validate_token("eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature")

            assert not result.is_valid
            assert result.error_code == "CERTIFICATE_ERROR"

    @pytest.mark.asyncio
    async def test_empty_token_validation(self, middleware):
        """Test validation with empty token string"""
        result = await middleware.validate_token("   ")

        assert not result.is_valid
        assert result.error_code == "MISSING_TOKEN"

    @pytest.mark.asyncio
    async def test_malformed_jwt_validation(self, middleware):
        """Test validation with malformed JWT structure"""
        result = await middleware.validate_token("invalid.token")

        assert not result.is_valid
        assert result.error_code == "MALFORMED_TOKEN"

    @pytest.mark.asyncio
    async def test_short_token_validation(self, middleware):
        """Test validation with token that's too short"""
        result = await middleware.validate_token("abc.def.ghi")

        assert not result.is_valid
        assert result.error_code == "MALFORMED_TOKEN"

    @pytest.mark.asyncio
    async def test_connection_error_validation(self, middleware):
        """Test handling of connection errors during validation"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = ConnectionError("Connection failed")

            result = await middleware.validate_token("eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature")

            assert not result.is_valid
            assert result.error_code == "SERVICE_UNAVAILABLE"


class TestFirebaseAuthRequired:
    """Test FirebaseAuthRequired dependency"""

    @pytest.fixture
    def auth_dependency(self):
        """Create auth dependency for testing"""
        return FirebaseAuthRequired()

    @pytest.fixture
    def auth_dependency_verified(self):
        """Create auth dependency requiring verified email"""
        return FirebaseAuthRequired(require_verified_email=True)

    @pytest.mark.asyncio
    async def test_successful_authentication(self, auth_dependency):
        """Test successful authentication"""
        mock_request = Mock()
        mock_request.headers = {"authorization": "Bearer valid_token"}

        with patch.object(auth_dependency.middleware, 'validate_token') as mock_validate:
            mock_firebase_user = FirebaseUser(
                uid="test_user",
                email="test@example.com",
                email_verified=True
            )
            mock_validate.return_value.is_valid = True
            mock_validate.return_value.firebase_user = mock_firebase_user

            # Mock the security dependency
            with patch.object(auth_dependency.middleware, 'security') as mock_security:
                mock_credentials = Mock()
                mock_credentials.credentials = "valid_token"
                mock_security.return_value = mock_credentials

                result = await auth_dependency(mock_request)

                assert result.uid == "test_user"
                assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_missing_token(self, auth_dependency):
        """Test authentication with missing token"""
        mock_request = Mock()

        with patch.object(auth_dependency.middleware, 'security') as mock_security:
            mock_security.return_value = None

            with pytest.raises(AuthError) as exc_info:
                await auth_dependency(mock_request)

            assert exc_info.value.error_code == "AUTH_REQUIRED"
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_email_verification_required(self, auth_dependency_verified):
        """Test email verification requirement"""
        mock_request = Mock()

        mock_firebase_user = FirebaseUser(
            uid="test_user",
            email="test@example.com",
            email_verified=False
        )

        with patch.object(auth_dependency_verified.middleware, 'security') as mock_security:
            mock_credentials = Mock()
            mock_credentials.credentials = "valid_token"
            mock_security.return_value = mock_credentials

            with patch.object(auth_dependency_verified.middleware, 'validate_token') as mock_validate:
                mock_validate.return_value.is_valid = True
                mock_validate.return_value.firebase_user = mock_firebase_user

                with pytest.raises(AuthError) as exc_info:
                    await auth_dependency_verified(mock_request)

                assert exc_info.value.error_code == "EMAIL_NOT_VERIFIED"
                assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestFirebaseInitialization:
    """Test Firebase initialization"""

    @patch.dict(os.environ, {"FIREBASE_PROJECT_ID": "test-project"})
    def test_initialize_firebase_with_service_account(self):
        """Test Firebase initialization with service account"""
        with patch('os.path.exists') as mock_exists, \
             patch('firebase_admin.credentials.Certificate') as mock_cert, \
             patch('firebase_admin.initialize_app') as mock_init:

            mock_exists.return_value = True
            mock_app = Mock()
            mock_init.return_value = mock_app

            # Set environment variables
            with patch.dict(os.environ, {
                "FIREBASE_SERVICE_ACCOUNT_KEY_PATH": "/path/to/key.json"
            }):
                result = initialize_firebase()

                assert result == mock_app
                mock_cert.assert_called_once_with("/path/to/key.json")
                mock_init.assert_called_once()

    @patch.dict(os.environ, {"FIREBASE_PROJECT_ID": "test-project"})
    def test_initialize_firebase_with_default_credentials(self):
        """Test Firebase initialization with default credentials"""
        with patch('os.path.exists') as mock_exists, \
             patch('firebase_admin.credentials.ApplicationDefault') as mock_default, \
             patch('firebase_admin.initialize_app') as mock_init:

            mock_exists.return_value = False
            mock_app = Mock()
            mock_init.return_value = mock_app

            result = initialize_firebase()

            assert result == mock_app
            mock_default.assert_called_once()
            mock_init.assert_called_once()

    def test_initialize_firebase_failure(self):
        """Test Firebase initialization failure"""
        with patch('firebase_admin.initialize_app') as mock_init:
            mock_init.side_effect = Exception("Firebase init failed")

            with pytest.raises(RuntimeError) as exc_info:
                initialize_firebase()

            assert "Firebase initialization failed" in str(exc_info.value)


class TestEndpointIntegration:
    """Test middleware integration with FastAPI endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(test_app)

    def test_protected_endpoint_without_token(self, client):
        """Test protected endpoint without token"""
        response = client.get("/protected")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test protected endpoint with invalid token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")

            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer invalid_token"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "INVALID_TOKEN"

    def test_protected_endpoint_with_valid_token(self, client):
        """Test protected endpoint with valid token"""
        sample_token = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "name": "Test User",
            "email_verified": True,
            "firebase": {"identities": {}},
            "custom_claims": {}
        }

        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.return_value = sample_token

            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == "test_user_123"
            assert data["email"] == "test@example.com"

    def test_optional_endpoint_without_token(self, client):
        """Test optional auth endpoint without token"""
        response = client.get("/optional")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["authenticated"] is False

    def test_optional_endpoint_with_token(self, client):
        """Test optional auth endpoint with token"""
        sample_token = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "email_verified": True,
            "firebase": {"identities": {}},
            "custom_claims": {}
        }

        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.return_value = sample_token

            response = client.get(
                "/optional",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["authenticated"] is True
            assert data["user_id"] == "test_user_123"

    def test_public_endpoint(self, client):
        """Test public endpoint (no auth required)"""
        response = client.get("/public")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "public endpoint"


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(test_app)

    def test_malformed_authorization_header(self, client):
        """Test malformed authorization header"""
        response = client.get(
            "/protected",
            headers={"Authorization": "InvalidFormat"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_token(self, client):
        """Test empty token in authorization header"""
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer "}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "EMPTY_TOKEN"

    def test_very_short_token(self, client):
        """Test token that's too short to be valid"""
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer abc"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "MALFORMED_TOKEN"

    def test_malformed_jwt_structure(self, client):
        """Test token without proper JWT structure"""
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.token.without.proper.structure"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "MALFORMED_TOKEN"

    def test_token_with_wrong_dot_count(self, client):
        """Test token with incorrect number of dots"""
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "MALFORMED_TOKEN"

    def test_expired_token_error_response(self, client):
        """Test expired token error response format"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired", Exception("test cause"))

            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer expired_token"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "EXPIRED_TOKEN"
            assert "timestamp" in error_data["error"]
            assert error_data["error"]["status"] == 401

    def test_network_error_handling(self, client):
        """Test network error handling"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = Exception("Network error")

            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "VALIDATION_ERROR"

    def test_connection_error_handling(self, client):
        """Test Firebase connection error handling"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = ConnectionError("Firebase unreachable")

            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "SERVICE_UNAVAILABLE"

    def test_timeout_error_handling(self, client):
        """Test Firebase timeout error handling"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = TimeoutError("Request timeout")

            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "SERVICE_TIMEOUT"

    def test_value_error_handling(self, client):
        """Test value error handling for token format issues"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = ValueError("Token format error")

            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.test-signature"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "MALFORMED_TOKEN"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])