"""
Comprehensive tests for the Onboarding API endpoints.

This module tests all onboarding-related API endpoints including:
- Public endpoints (sports, teams)
- Protected endpoints (status, step updates, completion)
- Authentication and authorization
- Request/response validation
- Error handling and edge cases
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from httpx import AsyncClient
from fastapi import status

from backend.models.users import User
from backend.models.sports import Sport, Team


class TestOnboardingSportsEndpoint:
    """Test GET /onboarding/sports endpoint."""

    async def test_get_sports_success(self, test_client: AsyncClient, test_sports: list[Sport]):
        """Test successful retrieval of sports list."""
        response = await test_client.get("/api/v1/onboarding/sports")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "sports" in data
        assert "total" in data
        assert isinstance(data["sports"], list)
        assert data["total"] == 3  # Only active sports

        # Check sports data (excluding inactive hockey)
        sports = data["sports"]
        assert len(sports) == 3

        # Verify sports are ordered by popularity rank
        ranks = [sport["popularity_rank"] for sport in sports]
        assert ranks == sorted(ranks)

        # Check first sport structure
        first_sport = sports[0]
        required_fields = [
            "id", "name", "slug", "icon", "icon_url",
            "description", "popularity_rank", "is_active"
        ]
        for field in required_fields:
            assert field in first_sport

        # Verify specific sport data
        football_sport = next(s for s in sports if s["name"] == "Football")
        assert football_sport["slug"] == "football"
        assert football_sport["icon"] == "🏈"
        assert football_sport["popularity_rank"] == 1
        assert football_sport["is_active"] is True

    async def test_get_sports_no_auth_required(self, test_client: AsyncClient, test_sports: list[Sport]):
        """Test that sports endpoint doesn't require authentication."""
        response = await test_client.get("/api/v1/onboarding/sports")
        assert response.status_code == status.HTTP_200_OK

    async def test_get_sports_empty_database(self, test_client: AsyncClient):
        """Test sports endpoint with no sports in database."""
        response = await test_client.get("/api/v1/onboarding/sports")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sports"] == []
        assert data["total"] == 0

    async def test_get_sports_performance(self, test_client: AsyncClient, test_sports: list[Sport], performance_threshold):
        """Test sports endpoint response time."""
        import time

        start_time = time.time()
        response = await test_client.get("/api/v1/onboarding/sports")
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        response_time = end_time - start_time
        assert response_time < performance_threshold["acceptable"]


class TestOnboardingTeamsEndpoint:
    """Test GET /onboarding/teams endpoint."""

    async def test_get_teams_single_sport(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team]):
        """Test getting teams for a single sport."""
        football_sport_id = str(test_sports[0].id)  # Football

        response = await test_client.get(
            f"/api/v1/onboarding/teams?sport_ids={football_sport_id}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "teams" in data
        assert "total" in data
        assert "sport_ids" in data

        teams = data["teams"]
        assert len(teams) == 2  # Patriots and Chiefs
        assert data["total"] == 2

        # Verify all teams belong to football
        for team in teams:
            assert team["sport_id"] == football_sport_id

        # Check team structure
        first_team = teams[0]
        required_fields = [
            "id", "name", "market", "slug", "sport_id",
            "logo_url", "abbreviation", "primary_color", "secondary_color"
        ]
        for field in required_fields:
            assert field in first_team

    async def test_get_teams_multiple_sports(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team]):
        """Test getting teams for multiple sports."""
        football_id = str(test_sports[0].id)  # Football
        basketball_id = str(test_sports[1].id)  # Basketball

        response = await test_client.get(
            f"/api/v1/onboarding/teams?sport_ids={football_id},{basketball_id}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        teams = data["teams"]
        assert len(teams) == 4  # All teams
        assert data["total"] == 4

        # Verify teams belong to requested sports
        sport_ids = {team["sport_id"] for team in teams}
        assert sport_ids == {football_id, basketball_id}

    async def test_get_teams_comma_separated_ids(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team]):
        """Test teams endpoint with comma-separated sport IDs in single parameter."""
        sport_ids = f"{test_sports[0].id},{test_sports[1].id}"

        response = await test_client.get(
            f"/api/v1/onboarding/teams?sport_ids={sport_ids}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["teams"]) == 4

    async def test_get_teams_url_encoded_comma_separated_ids(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team]):
        """Test teams endpoint with URL-encoded comma-separated sport IDs (the specific failing case)."""
        # This tests the exact failing URL format: sport_ids=nfl%2Cnba%2Cmlb%2Cnhl
        sport_ids_encoded = f"{test_sports[0].id}%2C{test_sports[1].id}"

        response = await test_client.get(
            f"/api/v1/onboarding/teams?sport_ids={sport_ids_encoded}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["teams"]) == 4
        assert data["total"] == 4

        # Verify teams belong to requested sports
        sport_ids = {team["sport_id"] for team in data["teams"]}
        expected_ids = {str(test_sports[0].id), str(test_sports[1].id)}
        assert sport_ids == expected_ids

    async def test_get_teams_mixed_format_compatibility(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team]):
        """Test teams endpoint maintains backward compatibility with array format."""
        football_id = str(test_sports[0].id)
        basketball_id = str(test_sports[1].id)

        # Test traditional array format (?sport_ids=uuid1&sport_ids=uuid2)
        response = await test_client.get(
            f"/api/v1/onboarding/teams?sport_ids={football_id}&sport_ids={basketball_id}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["teams"]) == 4

        # Verify teams belong to requested sports
        sport_ids = {team["sport_id"] for team in data["teams"]}
        expected_ids = {football_id, basketball_id}
        assert sport_ids == expected_ids

    async def test_get_teams_invalid_sport_id(self, test_client: AsyncClient):
        """Test teams endpoint with invalid sport ID format."""
        response = await test_client.get(
            "/api/v1/onboarding/teams?sport_ids=invalid-uuid"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "Invalid sport ID format" in data["detail"]

    async def test_get_teams_nonexistent_sport_id(self, test_client: AsyncClient):
        """Test teams endpoint with non-existent sport ID."""
        fake_uuid = str(uuid4())

        response = await test_client.get(
            f"/api/v1/onboarding/teams?sport_ids={fake_uuid}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["teams"] == []
        assert data["total"] == 0

    async def test_get_teams_missing_sport_ids(self, test_client: AsyncClient):
        """Test teams endpoint without sport_ids parameter."""
        response = await test_client.get("/api/v1/onboarding/teams")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_teams_empty_sport_ids(self, test_client: AsyncClient):
        """Test teams endpoint with empty sport_ids parameter."""
        response = await test_client.get("/api/v1/onboarding/teams?sport_ids=")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "At least one sport ID is required" in data["detail"]

    async def test_get_teams_no_auth_required(self, test_client: AsyncClient, test_sports: list[Sport]):
        """Test that teams endpoint doesn't require authentication."""
        response = await test_client.get(
            f"/api/v1/onboarding/teams?sport_ids={test_sports[0].id}"
        )
        assert response.status_code == status.HTTP_200_OK


class TestOnboardingStatusEndpoint:
    """Test GET /onboarding/status endpoint (requires authentication)."""

    async def test_get_status_authenticated(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test getting onboarding status for authenticated user."""
        response = await test_client.get(
            "/api/v1/onboarding/status",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        required_fields = ["is_onboarded", "current_step", "onboarding_completed_at"]
        for field in required_fields:
            assert field in data

        # Check values for incomplete onboarding
        assert data["is_onboarded"] is False
        assert data["current_step"] == 1
        assert data["onboarding_completed_at"] is None

    async def test_get_status_completed_user(self, test_client: AsyncClient, completed_onboarding_user: User, mock_firebase_auth):
        """Test getting status for user who completed onboarding."""
        # Mock for completed user
        with pytest.mock.patch('backend.api.services.user_service.get_current_db_user') as mock_get_user:
            mock_get_user.return_value = completed_onboarding_user

            response = await test_client.get(
                "/api/v1/onboarding/status",
                headers={"Authorization": "Bearer mock-token"}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["is_onboarded"] is True
        assert data["current_step"] is None
        assert data["onboarding_completed_at"] is not None

    async def test_get_status_unauthenticated(self, test_client: AsyncClient):
        """Test status endpoint without authentication."""
        response = await test_client.get("/api/v1/onboarding/status")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_status_invalid_token(self, test_client: AsyncClient):
        """Test status endpoint with invalid token."""
        response = await test_client.get(
            "/api/v1/onboarding/status",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOnboardingStepUpdateEndpoint:
    """Test PUT /onboarding/step endpoint."""

    async def test_update_step_valid(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test updating onboarding step with valid data."""
        response = await test_client.put(
            "/api/v1/onboarding/step",
            headers=authenticated_headers,
            json={"step": 2}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["current_step"] == 2
        assert data["is_onboarded"] is False

    async def test_update_step_all_valid_steps(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test updating to each valid step (1-5)."""
        for step in range(1, 6):
            response = await test_client.put(
                "/api/v1/onboarding/step",
                headers=authenticated_headers,
                json={"step": step}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["current_step"] == step

    async def test_update_step_invalid_low(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test updating step with value too low."""
        response = await test_client.put(
            "/api/v1/onboarding/step",
            headers=authenticated_headers,
            json={"step": 0}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Step must be between 1 and 5" in data["detail"]

    async def test_update_step_invalid_high(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test updating step with value too high."""
        response = await test_client.put(
            "/api/v1/onboarding/step",
            headers=authenticated_headers,
            json={"step": 6}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Step must be between 1 and 5" in data["detail"]

    async def test_update_step_invalid_type(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test updating step with invalid data type."""
        response = await test_client.put(
            "/api/v1/onboarding/step",
            headers=authenticated_headers,
            json={"step": "invalid"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_update_step_missing_data(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test updating step without required data."""
        response = await test_client.put(
            "/api/v1/onboarding/step",
            headers=authenticated_headers,
            json={}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_update_step_unauthenticated(self, test_client: AsyncClient):
        """Test step update without authentication."""
        response = await test_client.put(
            "/api/v1/onboarding/step",
            json={"step": 2}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOnboardingCompletionEndpoint:
    """Test POST /onboarding/complete endpoint."""

    async def test_complete_onboarding_force(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test completing onboarding with force flag."""
        response = await test_client.post(
            "/api/v1/onboarding/complete",
            headers=authenticated_headers,
            json={"force_complete": True}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["user_id"] == str(test_user.id)
        assert data["onboarding_completed_at"] is not None
        assert "successfully" in data["message"]

    async def test_complete_onboarding_without_preferences(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test completing onboarding without required preferences."""
        response = await test_client.post(
            "/api/v1/onboarding/complete",
            headers=authenticated_headers,
            json={"force_complete": False}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "sport preference" in data["detail"] or "team preference" in data["detail"]

    async def test_complete_onboarding_invalid_request(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test completing onboarding with invalid request data."""
        response = await test_client.post(
            "/api/v1/onboarding/complete",
            headers=authenticated_headers,
            json={"invalid_field": True}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_complete_onboarding_unauthenticated(self, test_client: AsyncClient):
        """Test completion endpoint without authentication."""
        response = await test_client.post(
            "/api/v1/onboarding/complete",
            json={"force_complete": True}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOnboardingResetEndpoint:
    """Test POST /onboarding/reset endpoint."""

    async def test_reset_onboarding(self, test_client: AsyncClient, completed_onboarding_user: User, mock_firebase_auth):
        """Test resetting onboarding for completed user."""
        with pytest.mock.patch('backend.api.services.user_service.get_current_db_user') as mock_get_user:
            mock_get_user.return_value = completed_onboarding_user

            response = await test_client.post(
                "/api/v1/onboarding/reset",
                headers={"Authorization": "Bearer mock-token"}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["is_onboarded"] is False
        assert data["current_step"] == 1
        assert data["onboarding_completed_at"] is None

    async def test_reset_onboarding_unauthenticated(self, test_client: AsyncClient):
        """Test reset endpoint without authentication."""
        response = await test_client.post("/api/v1/onboarding/reset")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOnboardingStatsEndpoint:
    """Test GET /onboarding/stats endpoint."""

    async def test_get_stats_authenticated(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test getting onboarding statistics."""
        response = await test_client.get(
            "/api/v1/onboarding/stats",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        required_fields = ["total_users", "completed_onboarding", "completion_rate", "step_distribution"]
        for field in required_fields:
            assert field in data

        # Check data types
        assert isinstance(data["total_users"], int)
        assert isinstance(data["completed_onboarding"], int)
        assert isinstance(data["completion_rate"], (int, float))
        assert isinstance(data["step_distribution"], dict)

        # Check step distribution structure
        for step in range(1, 6):
            assert f"step_{step}" in data["step_distribution"]

    async def test_get_stats_unauthenticated(self, test_client: AsyncClient):
        """Test stats endpoint without authentication."""
        response = await test_client.get("/api/v1/onboarding/stats")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOnboardingAPIPerformance:
    """Performance tests for onboarding API endpoints."""

    async def test_sports_endpoint_performance(self, test_client: AsyncClient, test_sports: list[Sport], performance_threshold):
        """Test sports endpoint performance under load."""
        import asyncio
        import time

        async def make_request():
            start_time = time.time()
            response = await test_client.get("/api/v1/onboarding/sports")
            end_time = time.time()
            return response.status_code, end_time - start_time

        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # Check all requests succeeded
        for status_code, response_time in results:
            assert status_code == status.HTTP_200_OK
            assert response_time < performance_threshold["acceptable"]

        # Check average response time
        avg_response_time = sum(rt for _, rt in results) / len(results)
        assert avg_response_time < performance_threshold["fast"]

    async def test_teams_endpoint_performance(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team], performance_threshold):
        """Test teams endpoint performance."""
        import time

        sport_id = str(test_sports[0].id)
        start_time = time.time()

        response = await test_client.get(f"/api/v1/onboarding/teams?sport_ids={sport_id}")

        end_time = time.time()
        response_time = end_time - start_time

        assert response.status_code == status.HTTP_200_OK
        assert response_time < performance_threshold["acceptable"]


class TestOnboardingAPIEdgeCases:
    """Edge case tests for onboarding API."""

    async def test_concurrent_step_updates(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth):
        """Test concurrent step updates for same user."""
        import asyncio

        async def update_step(step):
            return await test_client.put(
                "/api/v1/onboarding/step",
                headers=authenticated_headers,
                json={"step": step}
            )

        # Try to update to different steps concurrently
        tasks = [update_step(step) for step in [2, 3, 4]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # At least one should succeed
        success_count = sum(1 for result in results if hasattr(result, 'status_code') and result.status_code == 200)
        assert success_count >= 1

    async def test_large_sport_ids_list(self, test_client: AsyncClient, test_sports: list[Sport]):
        """Test teams endpoint with large number of sport IDs."""
        # Create a list with valid and invalid UUIDs
        sport_ids = [str(sport.id) for sport in test_sports]
        sport_ids.extend([str(uuid4()) for _ in range(50)])  # Add 50 fake UUIDs

        sport_ids_param = ",".join(sport_ids)

        response = await test_client.get(f"/api/v1/onboarding/teams?sport_ids={sport_ids_param}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only return teams for valid sport IDs
        assert len(data["teams"]) == 4  # Our test teams

    async def test_malformed_requests(self, test_client: AsyncClient, authenticated_headers, mock_firebase_auth):
        """Test API behavior with malformed requests."""
        # Test with malformed JSON
        response = await test_client.put(
            "/api/v1/onboarding/step",
            headers=authenticated_headers,
            content="invalid-json"
        )
        assert response.status_code in [400, 422]

        # Test with oversized request
        large_data = {"step": 2, "extra_data": "x" * 10000}
        response = await test_client.put(
            "/api/v1/onboarding/step",
            headers=authenticated_headers,
            json=large_data
        )
        # Should still work as we ignore extra fields
        assert response.status_code in [200, 422]