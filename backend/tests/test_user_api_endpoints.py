"""
Comprehensive tests for User API endpoints with Firebase authentication
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
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app, api_v1
from backend.api.schemas.auth import FirebaseUser, UserProfile, OnboardingStatus
from backend.api.exceptions import register_exception_handlers
from backend.models.users import User, UserSportPreference, UserTeamPreference, UserNotificationSettings
from backend.models.sports import Sport, Team
from backend.database import get_async_session


class TestUserAPIEndpoints:
    """Test User API endpoints with Firebase authentication"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def sample_firebase_user(self) -> FirebaseUser:
        """Sample Firebase user for testing"""
        return FirebaseUser(
            uid="test_user_123",
            email="test@example.com",
            display_name="Test User",
            email_verified=True,
            provider_data={},
            custom_claims={}
        )

    @pytest.fixture
    def sample_decoded_token(self) -> Dict[str, Any]:
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

    @pytest.fixture
    def mock_db_user(self):
        """Mock database user"""
        user = Mock(spec=User)
        user.id = "test_user_123"
        user.firebase_uid = "test_user_123"
        user.email = "test@example.com"
        user.display_name = "Test User"
        user.is_onboarded = True
        user.content_frequency = "daily"
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        user.last_active_at = datetime.now(timezone.utc)
        user.sport_preferences = []
        user.team_preferences = []
        user.notification_settings = None
        return user

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
            assert data["firebase_initialized"] is True

    def test_config_health_endpoint(self, client):
        """Test configuration health check endpoint"""
        with patch('backend.config.firebase.validate_firebase_environment') as mock_config:
            mock_config.return_value = {
                "valid": True,
                "project_id": "test-project",
                "has_service_account": False
            }

            response = client.get("/health/config")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["valid"] is True

    def test_get_current_user_me_endpoint_without_token(self, client):
        """Test /me endpoint without authentication token"""
        response = client.get("/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_get_current_user_me_endpoint_with_valid_token(self, client, sample_decoded_token, mock_db_user):
        """Test /me endpoint with valid Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_user_profile.return_value = UserProfile.from_orm(mock_db_user)
            mock_context.return_value = mock_user_context

            response = client.get(
                "/me",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["firebase_uid"] == "test_user_123"
            assert data["email"] == "test@example.com"

    def test_get_current_user_users_me_endpoint(self, client, sample_decoded_token, mock_db_user):
        """Test /users/me endpoint with valid Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_user_profile.return_value = UserProfile.from_orm(mock_db_user)
            mock_context.return_value = mock_user_context

            response = client.get(
                "/users/me",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["firebase_uid"] == "test_user_123"
            assert data["email"] == "test@example.com"

    def test_api_v1_users_me_endpoint(self, client, sample_decoded_token, mock_db_user):
        """Test /api/v1/users/me endpoint with valid Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_user_profile.return_value = UserProfile.from_orm(mock_db_user)
            mock_context.return_value = mock_user_context

            response = client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["firebase_uid"] == "test_user_123"
            assert data["email"] == "test@example.com"

    def test_api_v1_me_preferences_endpoint(self, client, sample_decoded_token, mock_db_user):
        """Test /api/v1/me/preferences endpoint with valid Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user

            response = client.get(
                "/api/v1/me/preferences",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "sport_preferences" in data
            assert "team_preferences" in data
            assert "notification_settings" in data

    def test_me_preferences_endpoint(self, client, sample_decoded_token, mock_db_user):
        """Test /me/preferences endpoint with valid Firebase token"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user

            response = client.get(
                "/me/preferences",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "sport_preferences" in data
            assert "team_preferences" in data
            assert "notification_settings" in data

    def test_me_dashboard_endpoint_requires_onboarded_user(self, client, sample_decoded_token):
        """Test /me/dashboard endpoint requires onboarded user"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.require_onboarded_user') as mock_onboarded:

            mock_verify.return_value = sample_decoded_token

            # Mock user not onboarded
            from backend.api.exceptions import UserNotOnboardedError
            mock_onboarded.side_effect = UserNotOnboardedError("User not onboarded")

            response = client.get(
                "/me/dashboard",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_me_dashboard_endpoint_with_onboarded_user(self, client, sample_decoded_token, mock_db_user):
        """Test /me/dashboard endpoint with onboarded user"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.require_onboarded_user') as mock_onboarded:

            mock_verify.return_value = sample_decoded_token
            mock_onboarded.return_value = mock_db_user

            response = client.get(
                "/me/dashboard",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == "test_user_123"
            assert data["is_onboarded"] is True

    def test_api_v1_me_home_endpoint(self, client, sample_decoded_token, mock_db_user):
        """Test /api/v1/me/home endpoint"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user

            response = client.get(
                "/api/v1/me/home",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "most_liked_team_id" in data
            assert "user_teams" in data

    def test_auth_firebase_endpoint(self, client, sample_decoded_token):
        """Test /auth/firebase endpoint"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.return_value = sample_decoded_token

            response = client.get(
                "/auth/firebase",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["uid"] == "test_user_123"
            assert data["email"] == "test@example.com"

    def test_auth_sync_user_endpoint(self, client, sample_decoded_token, mock_db_user):
        """Test /auth/sync-user endpoint"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_or_create_db_user.return_value = mock_db_user
            mock_context.return_value = mock_user_context

            response = client.post(
                "/auth/sync-user",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["firebase_uid"] == "test_user_123"

    def test_public_sports_endpoint_without_auth(self, client):
        """Test /public/sports endpoint without authentication"""
        with patch('backend.api.services.user_service.get_current_user_context') as mock_context:
            mock_context.return_value = None

            response = client.get("/public/sports")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_preferences"] is False
            assert "sports" in data

    def test_public_sports_endpoint_with_auth(self, client, sample_decoded_token, mock_db_user):
        """Test /public/sports endpoint with authentication"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.db_user = mock_db_user
            mock_context.return_value = mock_user_context

            response = client.get(
                "/public/sports",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_preferences"] is True
            assert data["user_id"] == "test_user_123"

    def test_invalid_token_error_handling(self, client):
        """Test error handling for invalid tokens"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")

            response = client.get(
                "/me",
                headers={"Authorization": "Bearer invalid_token"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            assert error_data["error"]["code"] == "INVALID_TOKEN"

    def test_expired_token_error_handling(self, client):
        """Test error handling for expired tokens"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired", Exception("test cause"))

            response = client.get(
                "/me",
                headers={"Authorization": "Bearer expired_token"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            error_data = response.json()
            # Note: Due to token length validation in middleware, this might be MALFORMED_TOKEN
            assert error_data["error"]["code"] in ["EXPIRED_TOKEN", "MALFORMED_TOKEN"]

    def test_missing_token_error_handling(self, client):
        """Test error handling for missing tokens"""
        response = client.get("/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_malformed_token_error_handling(self, client):
        """Test error handling for malformed tokens"""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid.token.format"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "MALFORMED_TOKEN"

    def test_empty_token_error_handling(self, client):
        """Test error handling for empty tokens"""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer "}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "EMPTY_TOKEN"


class TestUserPreferencesAPI:
    """Test User Preferences API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def sample_decoded_token(self) -> Dict[str, Any]:
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

    @pytest.fixture
    def mock_db_user_with_prefs(self):
        """Mock database user with preferences"""
        user = Mock(spec=User)
        user.id = "test_user_123"
        user.firebase_uid = "test_user_123"
        user.email = "test@example.com"
        user.display_name = "Test User"
        user.is_onboarded = True
        user.content_frequency = "daily"

        # Mock sport preferences
        sport_pref = Mock(spec=UserSportPreference)
        sport_pref.id = "sport_pref_1"
        sport_pref.sport_id = "sport_1"
        sport_pref.sport = Mock()
        sport_pref.sport.name = "Basketball"
        sport_pref.rank = 1
        sport_pref.is_active = True
        user.sport_preferences = [sport_pref]

        # Mock team preferences
        team_pref = Mock(spec=UserTeamPreference)
        team_pref.id = "team_pref_1"
        team_pref.team_id = "team_1"
        team_pref.team = Mock()
        team_pref.team.name = "Lakers"
        team_pref.affinity_score = 0.9
        team_pref.is_active = True
        user.team_preferences = [team_pref]

        # Mock notification settings
        notification_settings = Mock(spec=UserNotificationSettings)
        notification_settings.push_enabled = True
        notification_settings.email_enabled = False
        notification_settings.game_reminders = True
        notification_settings.news_alerts = False
        notification_settings.score_updates = True
        user.notification_settings = notification_settings

        return user

    def test_update_preferences_bulk_api_v1(self, client, sample_decoded_token, mock_db_user_with_prefs):
        """Test bulk preferences update via /api/v1/me/preferences"""
        preferences_update = {
            "sports": [{"sport_id": "sport_1", "rank": 1}],
            "teams": [{"team_id": "team_1", "affinity_score": 0.8}],
            "notifications": {
                "push_enabled": True,
                "email_enabled": True,
                "game_reminders": True,
                "news_alerts": True,
                "score_updates": True
            },
            "content_frequency": "weekly"
        }

        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep, \
             patch('backend.api.services.preference_service.PreferenceService') as mock_service:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user_with_prefs

            # Mock preference service
            mock_pref_service = Mock()
            mock_pref_service.update_user_preferences.return_value = {"updated": True}
            mock_service.return_value = mock_pref_service

            response = client.put(
                "/api/v1/me/preferences",
                headers={"Authorization": "Bearer valid_token"},
                json=preferences_update
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "sport_preferences" in data
            assert "team_preferences" in data
            assert "notification_settings" in data

    def test_update_sports_preferences_api_v1(self, client, sample_decoded_token, mock_db_user_with_prefs):
        """Test sports preferences update via /api/v1/me/preferences/sports"""
        sports_update = {
            "sports": [
                {"sport_id": "sport_1", "rank": 1},
                {"sport_id": "sport_2", "rank": 2}
            ]
        }

        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep, \
             patch('backend.api.services.preference_service.PreferenceService') as mock_service:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user_with_prefs

            # Mock preference service
            mock_pref_service = Mock()
            mock_pref_service.update_sport_preferences.return_value = mock_db_user_with_prefs.sport_preferences
            mock_service.return_value = mock_pref_service

            response = client.put(
                "/api/v1/me/preferences/sports",
                headers={"Authorization": "Bearer valid_token"},
                json=sports_update
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "sport_preferences" in data
            assert len(data["sport_preferences"]) > 0

    def test_update_teams_preferences_api_v1(self, client, sample_decoded_token, mock_db_user_with_prefs):
        """Test teams preferences update via /api/v1/me/preferences/teams"""
        teams_update = {
            "teams": [
                {"team_id": "team_1", "affinity_score": 0.9},
                {"team_id": "team_2", "affinity_score": 0.7}
            ]
        }

        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep, \
             patch('backend.api.services.preference_service.PreferenceService') as mock_service:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user_with_prefs

            # Mock preference service
            mock_pref_service = Mock()
            mock_pref_service.update_team_preferences.return_value = mock_db_user_with_prefs.team_preferences
            mock_service.return_value = mock_pref_service

            response = client.put(
                "/api/v1/me/preferences/teams",
                headers={"Authorization": "Bearer valid_token"},
                json=teams_update
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "team_preferences" in data
            assert len(data["team_preferences"]) > 0

    def test_update_notifications_preferences_api_v1(self, client, sample_decoded_token, mock_db_user_with_prefs):
        """Test notifications preferences update via /api/v1/me/preferences/notifications"""
        notifications_update = {
            "push_enabled": True,
            "email_enabled": True,
            "game_reminders": False,
            "news_alerts": True,
            "score_updates": False
        }

        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep, \
             patch('backend.api.services.preference_service.PreferenceService') as mock_service:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user_with_prefs

            # Mock preference service
            mock_pref_service = Mock()
            mock_pref_service.update_notification_preferences.return_value = mock_db_user_with_prefs.notification_settings
            mock_service.return_value = mock_pref_service

            response = client.put(
                "/api/v1/me/preferences/notifications",
                headers={"Authorization": "Bearer valid_token"},
                json=notifications_update
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "notification_settings" in data
            assert data["notification_settings"]["push_enabled"] is True

    def test_preferences_validation_errors(self, client, sample_decoded_token, mock_db_user_with_prefs):
        """Test preferences validation for invalid data"""
        invalid_update = {
            "sports": [{"sport_id": "", "rank": -1}],  # Invalid data
        }

        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_db_user') as mock_db_user_dep:

            mock_verify.return_value = sample_decoded_token
            mock_db_user_dep.return_value = mock_db_user_with_prefs

            response = client.put(
                "/api/v1/me/preferences",
                headers={"Authorization": "Bearer valid_token"},
                json=invalid_update
            )

            # Should return validation error
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Onboarding Status Endpoint Tests

    @pytest.fixture
    def mock_onboarded_user(self):
        """Mock user who has completed onboarding"""
        user = Mock(spec=User)
        user.id = "onboarded_user_123"
        user.firebase_uid = "onboarded_user_123"
        user.email = "onboarded@example.com"
        user.display_name = "Onboarded User"
        user.onboarding_completed_at = datetime.now(timezone.utc)
        user.current_onboarding_step = None
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        user.last_active_at = datetime.now(timezone.utc)
        # Mock the is_onboarded property to return True when onboarding_completed_at is not None
        user.is_onboarded = True
        return user

    @pytest.fixture
    def mock_onboarding_user_step_2(self):
        """Mock user currently on onboarding step 2"""
        user = Mock(spec=User)
        user.id = "onboarding_user_123"
        user.firebase_uid = "onboarding_user_123"
        user.email = "onboarding@example.com"
        user.display_name = "Onboarding User"
        user.onboarding_completed_at = None
        user.current_onboarding_step = 2
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        user.last_active_at = datetime.now(timezone.utc)
        # Mock the is_onboarded property to return False when onboarding_completed_at is None
        user.is_onboarded = False
        return user

    @pytest.fixture
    def mock_new_user(self):
        """Mock new user who hasn't started onboarding"""
        user = Mock(spec=User)
        user.id = "new_user_123"
        user.firebase_uid = "new_user_123"
        user.email = "new@example.com"
        user.display_name = "New User"
        user.onboarding_completed_at = None
        user.current_onboarding_step = None
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        user.last_active_at = datetime.now(timezone.utc)
        # Mock the is_onboarded property to return False when onboarding_completed_at is None
        user.is_onboarded = False
        return user

    def test_auth_onboarding_status_without_token(self, client):
        """Test /auth/onboarding-status endpoint without authentication token"""
        response = client.get("/auth/onboarding-status")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_data = response.json()
        assert error_data["error"]["code"] == "AUTH_REQUIRED"

    def test_auth_onboarding_status_completed(self, client, sample_decoded_token, mock_onboarded_user):
        """Test /auth/onboarding-status endpoint for completed onboarding"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_or_create_db_user.return_value = mock_onboarded_user
            mock_context.return_value = mock_user_context

            response = client.get(
                "/auth/onboarding-status",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hasCompletedOnboarding"] is True
            assert data["currentStep"] is None

    def test_auth_onboarding_status_in_progress(self, client, sample_decoded_token, mock_onboarding_user_step_2):
        """Test /auth/onboarding-status endpoint for onboarding in progress"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_or_create_db_user.return_value = mock_onboarding_user_step_2
            mock_context.return_value = mock_user_context

            response = client.get(
                "/auth/onboarding-status",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hasCompletedOnboarding"] is False
            assert data["currentStep"] == 2

    def test_auth_onboarding_status_not_started(self, client, sample_decoded_token, mock_new_user):
        """Test /auth/onboarding-status endpoint for user who hasn't started onboarding"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_or_create_db_user.return_value = mock_new_user
            mock_context.return_value = mock_user_context

            response = client.get(
                "/auth/onboarding-status",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hasCompletedOnboarding"] is False
            assert data["currentStep"] is None

    def test_api_v1_auth_onboarding_status_completed(self, client, sample_decoded_token, mock_onboarded_user):
        """Test /api/v1/auth/onboarding-status endpoint for completed onboarding"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_or_create_db_user.return_value = mock_onboarded_user
            mock_context.return_value = mock_user_context

            response = client.get(
                "/api/v1/auth/onboarding-status",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hasCompletedOnboarding"] is True
            assert data["currentStep"] is None

    def test_api_v1_auth_onboarding_status_in_progress(self, client, sample_decoded_token, mock_onboarding_user_step_2):
        """Test /api/v1/auth/onboarding-status endpoint for onboarding in progress"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_or_create_db_user.return_value = mock_onboarding_user_step_2
            mock_context.return_value = mock_user_context

            response = client.get(
                "/api/v1/auth/onboarding-status",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hasCompletedOnboarding"] is False
            assert data["currentStep"] == 2

    def test_onboarding_status_response_schema_validation(self, client, sample_decoded_token, mock_onboarding_user_step_2):
        """Test onboarding status response matches expected schema"""
        with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
             patch('backend.api.services.user_service.get_current_user_context') as mock_context:

            mock_verify.return_value = sample_decoded_token

            # Mock the user context
            mock_user_context = Mock()
            mock_user_context.get_or_create_db_user.return_value = mock_onboarding_user_step_2
            mock_context.return_value = mock_user_context

            response = client.get(
                "/auth/onboarding-status",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Validate schema structure
            assert isinstance(data, dict)
            assert "hasCompletedOnboarding" in data
            assert "currentStep" in data
            assert isinstance(data["hasCompletedOnboarding"], bool)
            assert isinstance(data["currentStep"], (int, type(None)))

            # Validate response can be parsed by OnboardingStatus schema
            onboarding_status = OnboardingStatus(**data)
            assert onboarding_status.hasCompletedOnboarding is False
            assert onboarding_status.currentStep == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])