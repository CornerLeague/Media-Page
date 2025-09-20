"""
Firebase Authentication Integration Tests

This module tests the Firebase authentication integration including:
- Firebase Admin SDK initialization
- JWT token validation
- Authentication middleware functionality
- Error handling for various Firebase exceptions
- Health check endpoints
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

import firebase_admin
from firebase_admin import auth
from fastapi import status

# Mock environment before imports to avoid configuration errors
@pytest.fixture(autouse=True)
def mock_firebase_environment():
    """Mock Firebase environment variables"""
    with patch.dict(os.environ, {
        "FIREBASE_PROJECT_ID": "test-project-id",
        "FIREBASE_SERVICE_ACCOUNT_KEY_PATH": "/path/to/test-key.json"
    }):
        yield


class TestFirebaseIntegration:
    """Test Firebase authentication integration"""

    def test_firebase_admin_sdk_initialization_with_service_account(self):
        """Test Firebase Admin SDK initialization with service account"""
        from backend.api.middleware.auth import initialize_firebase

        with patch('os.path.exists') as mock_exists, \
             patch('firebase_admin.credentials.Certificate') as mock_cert, \
             patch('firebase_admin.initialize_app') as mock_init:

            mock_exists.return_value = True
            mock_app = Mock()
            mock_init.return_value = mock_app

            result = initialize_firebase()

            assert result == mock_app
            mock_cert.assert_called_once_with("/path/to/test-key.json")
            mock_init.assert_called_once()

    def test_firebase_admin_sdk_initialization_with_default_credentials(self):
        """Test Firebase Admin SDK initialization with default credentials"""
        from backend.api.middleware.auth import initialize_firebase

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

    def test_firebase_initialization_failure(self):
        """Test Firebase initialization failure handling"""
        from backend.api.middleware.auth import initialize_firebase

        with patch('firebase_admin.initialize_app') as mock_init:
            mock_init.side_effect = Exception("Firebase init failed")

            with pytest.raises(RuntimeError) as exc_info:
                initialize_firebase()

            assert "Firebase initialization failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_jwt_middleware_valid_token(self):
        """Test JWT middleware with valid Firebase token"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware
        from backend.api.schemas.auth import FirebaseUser

        middleware = FirebaseJWTMiddleware()

        # Mock request with valid token
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "valid_firebase_jwt_token_that_is_long_enough_to_pass_validation_checks_and_has_proper_jwt_structure.with.signature"

        sample_decoded_token = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg",
            "email_verified": True,
            "firebase": {"identities": {"email": ["test@example.com"]}},
            "custom_claims": {"role": "user"}
        }

        with patch.object(middleware, 'security') as mock_security, \
             patch('firebase_admin.auth.verify_id_token') as mock_verify:

            mock_security.return_value = mock_credentials
            mock_verify.return_value = sample_decoded_token

            result = await middleware(mock_request)

            assert result is not None
            assert isinstance(result, FirebaseUser)
            assert result.uid == "test_user_123"
            assert result.email == "test@example.com"
            assert result.email_verified is True

    @pytest.mark.asyncio
    async def test_jwt_middleware_no_token(self):
        """Test JWT middleware with no token provided"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()

        with patch.object(middleware, 'security') as mock_security:
            mock_security.return_value = None

            result = await middleware(mock_request)

            assert result is None

    @pytest.mark.asyncio
    async def test_jwt_middleware_empty_token(self):
        """Test JWT middleware with empty token"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware, AuthError

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = ""

        with patch.object(middleware, 'security') as mock_security:
            mock_security.return_value = mock_credentials

            with pytest.raises(AuthError) as exc_info:
                await middleware(mock_request)

            assert exc_info.value.error_code == "EMPTY_TOKEN"
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_jwt_middleware_malformed_token(self):
        """Test JWT middleware with malformed token"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware, AuthError

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "short_token"

        with patch.object(middleware, 'security') as mock_security:
            mock_security.return_value = mock_credentials

            with pytest.raises(AuthError) as exc_info:
                await middleware(mock_request)

            assert exc_info.value.error_code == "MALFORMED_TOKEN"
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_jwt_middleware_expired_token(self):
        """Test JWT middleware with expired Firebase token"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware, AuthError

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.expired_signature"

        with patch.object(middleware, 'security') as mock_security, \
             patch('firebase_admin.auth.verify_id_token') as mock_verify:

            mock_security.return_value = mock_credentials
            mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired", Exception("test cause"))

            with pytest.raises(AuthError) as exc_info:
                await middleware(mock_request)

            assert exc_info.value.error_code == "EXPIRED_TOKEN"

    @pytest.mark.asyncio
    async def test_jwt_middleware_revoked_token(self):
        """Test JWT middleware with revoked Firebase token"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware, AuthError

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.revoked_signature"

        with patch.object(middleware, 'security') as mock_security, \
             patch('firebase_admin.auth.verify_id_token') as mock_verify:

            mock_security.return_value = mock_credentials
            mock_verify.side_effect = auth.RevokedIdTokenError("Token revoked")

            with pytest.raises(AuthError) as exc_info:
                await middleware(mock_request)

            assert exc_info.value.error_code == "REVOKED_TOKEN"

    @pytest.mark.asyncio
    async def test_jwt_middleware_invalid_token(self):
        """Test JWT middleware with invalid Firebase token"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware, AuthError

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.invalid_signature"

        with patch.object(middleware, 'security') as mock_security, \
             patch('firebase_admin.auth.verify_id_token') as mock_verify:

            mock_security.return_value = mock_credentials
            mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")

            with pytest.raises(AuthError) as exc_info:
                await middleware(mock_request)

            assert exc_info.value.error_code == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_jwt_middleware_certificate_fetch_error(self):
        """Test JWT middleware with certificate fetch error"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware, AuthError

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.certificate_error_signature"

        with patch.object(middleware, 'security') as mock_security, \
             patch('firebase_admin.auth.verify_id_token') as mock_verify:

            mock_security.return_value = mock_credentials
            mock_verify.side_effect = auth.CertificateFetchError("Certificate error", Exception("test cause"))

            with pytest.raises(AuthError) as exc_info:
                await middleware(mock_request)

            assert exc_info.value.error_code == "CERTIFICATE_ERROR"

    @pytest.mark.asyncio
    async def test_jwt_middleware_connection_error(self):
        """Test JWT middleware with connection error"""
        from backend.api.middleware.auth import FirebaseJWTMiddleware, AuthError

        middleware = FirebaseJWTMiddleware()
        mock_request = Mock()
        mock_credentials = Mock()
        mock_credentials.credentials = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJ0ZXN0LXByb2plY3QiLCJhdXRoX3RpbWUiOjE2NDE5NzYwMDAsImV4cCI6MTY0MTk3OTYwMCwiaWF0IjoxNjQxOTc2MDAwLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwibmFtZSI6IlRlc3QgVXNlciIsInVpZCI6InRlc3RfdXNlcl8xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.connection_error_signature"

        with patch.object(middleware, 'security') as mock_security, \
             patch('firebase_admin.auth.verify_id_token') as mock_verify:

            mock_security.return_value = mock_credentials
            mock_verify.side_effect = ConnectionError("Firebase unreachable")

            with pytest.raises(AuthError) as exc_info:
                await middleware(mock_request)

            assert exc_info.value.error_code == "SERVICE_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_firebase_auth_required_dependency(self):
        """Test FirebaseAuthRequired dependency"""
        from backend.api.middleware.auth import FirebaseAuthRequired
        from backend.api.schemas.auth import FirebaseUser

        auth_dependency = FirebaseAuthRequired()
        mock_request = Mock()

        mock_firebase_user = FirebaseUser(
            uid="test_user",
            email="test@example.com",
            email_verified=True
        )

        with patch.object(auth_dependency.middleware, '__call__') as mock_middleware:
            mock_middleware.return_value = mock_firebase_user

            result = await auth_dependency(mock_request)

            assert result.uid == "test_user"
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_firebase_auth_required_no_user(self):
        """Test FirebaseAuthRequired dependency with no user"""
        from backend.api.middleware.auth import FirebaseAuthRequired, AuthError

        auth_dependency = FirebaseAuthRequired()
        mock_request = Mock()

        with patch.object(auth_dependency.middleware, '__call__') as mock_middleware:
            mock_middleware.return_value = None

            with pytest.raises(AuthError) as exc_info:
                await auth_dependency(mock_request)

            assert exc_info.value.error_code == "AUTH_REQUIRED"
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_firebase_auth_optional_dependency(self):
        """Test FirebaseAuthOptional dependency"""
        from backend.api.middleware.auth import FirebaseAuthOptional
        from backend.api.schemas.auth import FirebaseUser

        auth_dependency = FirebaseAuthOptional()
        mock_request = Mock()

        mock_firebase_user = FirebaseUser(
            uid="test_user",
            email="test@example.com",
            email_verified=True
        )

        with patch.object(auth_dependency.middleware, '__call__') as mock_middleware:
            mock_middleware.return_value = mock_firebase_user

            result = await auth_dependency(mock_request)

            assert result.uid == "test_user"
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_firebase_auth_optional_no_user(self):
        """Test FirebaseAuthOptional dependency with no user"""
        from backend.api.middleware.auth import FirebaseAuthOptional, AuthError

        auth_dependency = FirebaseAuthOptional()
        mock_request = Mock()

        with patch.object(auth_dependency.middleware, '__call__') as mock_middleware:
            mock_middleware.side_effect = AuthError(error_code="INVALID_TOKEN")

            result = await auth_dependency(mock_request)

            assert result is None

    @pytest.mark.asyncio
    async def test_firebase_health_check_success(self):
        """Test Firebase health check success"""
        from backend.api.middleware.auth import check_firebase_health

        with patch('firebase_admin.auth.get_user') as mock_get_user:
            mock_get_user.side_effect = auth.UserNotFoundError("User not found")

            result = await check_firebase_health()

            assert result["status"] == "healthy"
            assert result["firebase_initialized"] is not None
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_firebase_health_check_failure(self):
        """Test Firebase health check failure"""
        from backend.api.middleware.auth import check_firebase_health

        with patch('firebase_admin.auth.get_user') as mock_get_user:
            mock_get_user.side_effect = Exception("Firebase connection failed")

            result = await check_firebase_health()

            assert result["status"] == "unhealthy"
            assert "error" in result
            assert "timestamp" in result


class TestFirebaseConfigValidation:
    """Test Firebase configuration validation"""

    def test_firebase_config_validation_success(self):
        """Test successful Firebase configuration validation"""
        from backend.config.firebase import validate_firebase_environment

        with patch.dict(os.environ, {
            "FIREBASE_PROJECT_ID": "test-project",
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json"
        }):
            result = validate_firebase_environment()

            assert result["valid"] is True
            assert result["project_id"] == "test-project"

    def test_firebase_config_validation_failure(self):
        """Test Firebase configuration validation failure"""
        from backend.config.firebase import validate_firebase_environment

        with patch.dict(os.environ, {}, clear=True):
            result = validate_firebase_environment()

            assert result["valid"] is False
            assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])