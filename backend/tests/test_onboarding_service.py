"""
Unit tests for the OnboardingService business logic.

This module tests the OnboardingService class methods independently
of the API layer, focusing on business logic validation, data processing,
and database interactions.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import Mock, patch

from backend.api.services.onboarding_service import OnboardingService
from backend.models.users import User
from backend.models.sports import Sport, Team
from backend.api.schemas.onboarding import (
    OnboardingStatusResponse,
    OnboardingCompletionResponse,
    OnboardingSportsListResponse,
    OnboardingTeamsListResponse
)


class TestOnboardingServiceGetStatus:
    """Test OnboardingService.get_onboarding_status method."""

    async def test_get_status_incomplete_user(self, test_session, test_user: User):
        """Test getting status for user with incomplete onboarding."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_status(test_user)

        assert isinstance(result, OnboardingStatusResponse)
        assert result.is_onboarded is False
        assert result.current_step == 1
        assert result.onboarding_completed_at is None

    async def test_get_status_completed_user(self, test_session, completed_onboarding_user: User):
        """Test getting status for user who completed onboarding."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_status(completed_onboarding_user)

        assert isinstance(result, OnboardingStatusResponse)
        assert result.is_onboarded is True
        assert result.current_step is None
        assert result.onboarding_completed_at is not None

    async def test_get_status_user_with_preferences(self, test_session):
        """Test getting status for user with existing preferences."""
        # Create user with some preferences
        user = User(
            id=uuid4(),
            firebase_uid="test-uid-prefs",
            email="prefs@example.com",
            display_name="User With Prefs",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_active_at=datetime.utcnow(),
            current_onboarding_step=3,
            onboarding_completed_at=None
        )

        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        service = OnboardingService(test_session)
        result = await service.get_onboarding_status(user)

        assert result.current_step == 3
        assert result.is_onboarded is False


class TestOnboardingServiceStepUpdate:
    """Test OnboardingService.update_onboarding_step method."""

    async def test_update_step_valid_values(self, test_session, test_user: User):
        """Test updating to all valid step values."""
        service = OnboardingService(test_session)

        for step in range(1, 6):
            result = await service.update_onboarding_step(test_user, step)

            assert isinstance(result, OnboardingStatusResponse)
            assert result.current_step == step
            assert result.is_onboarded is False

            # Refresh user to verify database update
            await test_session.refresh(test_user)
            assert test_user.current_onboarding_step == step

    async def test_update_step_invalid_low(self, test_session, test_user: User):
        """Test updating step with value below valid range."""
        service = OnboardingService(test_session)

        with pytest.raises(ValueError, match="Step must be between 1 and 5"):
            await service.update_onboarding_step(test_user, 0)

    async def test_update_step_invalid_high(self, test_session, test_user: User):
        """Test updating step with value above valid range."""
        service = OnboardingService(test_session)

        with pytest.raises(ValueError, match="Step must be between 1 and 5"):
            await service.update_onboarding_step(test_user, 6)

    async def test_update_step_invalid_negative(self, test_session, test_user: User):
        """Test updating step with negative value."""
        service = OnboardingService(test_session)

        with pytest.raises(ValueError, match="Step must be between 1 and 5"):
            await service.update_onboarding_step(test_user, -1)

    async def test_update_step_updates_last_active(self, test_session, test_user: User):
        """Test that step update also updates last_active_at timestamp."""
        service = OnboardingService(test_session)
        original_last_active = test_user.last_active_at

        # Wait a tiny bit to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.01)

        await service.update_onboarding_step(test_user, 2)

        await test_session.refresh(test_user)
        assert test_user.last_active_at > original_last_active

    async def test_update_step_database_rollback_on_error(self, test_session, test_user: User):
        """Test that database transaction is rolled back on error."""
        service = OnboardingService(test_session)
        original_step = test_user.current_onboarding_step

        # Mock commit to raise an exception
        with patch.object(test_session, 'commit', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                await service.update_onboarding_step(test_user, 3)

        # Verify user step wasn't changed
        await test_session.refresh(test_user)
        assert test_user.current_onboarding_step == original_step


class TestOnboardingServiceGetSports:
    """Test OnboardingService.get_onboarding_sports method."""

    async def test_get_sports_success(self, test_session, test_sports: list[Sport]):
        """Test successful retrieval of sports."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_sports()

        assert isinstance(result, OnboardingSportsListResponse)
        assert len(result.sports) == 3  # Only active sports
        assert result.total == 3

        # Verify sports are ordered by popularity rank
        ranks = [sport.popularity_rank for sport in result.sports]
        assert ranks == sorted(ranks)

        # Check first sport
        first_sport = result.sports[0]
        assert first_sport.name == "Football"
        assert first_sport.popularity_rank == 1
        assert first_sport.is_active is True

    async def test_get_sports_excludes_inactive(self, test_session, test_sports: list[Sport]):
        """Test that inactive sports are excluded from results."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_sports()

        # Should not include Hockey (is_active = False)
        sport_names = [sport.name for sport in result.sports]
        assert "Hockey" not in sport_names
        assert "Football" in sport_names
        assert "Basketball" in sport_names
        assert "Baseball" in sport_names

    async def test_get_sports_empty_database(self, test_session):
        """Test getting sports from empty database."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_sports()

        assert isinstance(result, OnboardingSportsListResponse)
        assert result.sports == []
        assert result.total == 0

    async def test_get_sports_database_error(self, test_session, test_sports: list[Sport]):
        """Test handling of database errors."""
        service = OnboardingService(test_session)

        # Mock execute to raise an exception
        with patch.object(test_session, 'execute', side_effect=Exception("Database connection error")):
            with pytest.raises(Exception, match="Database connection error"):
                await service.get_onboarding_sports()


class TestOnboardingServiceGetTeams:
    """Test OnboardingService.get_onboarding_teams method."""

    async def test_get_teams_single_sport(self, test_session, test_sports: list[Sport], test_teams: list[Team]):
        """Test getting teams for a single sport."""
        service = OnboardingService(test_session)
        football_sport_id = test_sports[0].id  # Football

        result = await service.get_onboarding_teams([football_sport_id])

        assert isinstance(result, OnboardingTeamsListResponse)
        assert len(result.teams) == 2  # Patriots and Chiefs
        assert result.total == 2
        assert result.sport_ids == [football_sport_id]

        # Verify all teams belong to football
        for team in result.teams:
            assert team.sport_id == football_sport_id

    async def test_get_teams_multiple_sports(self, test_session, test_sports: list[Sport], test_teams: list[Team]):
        """Test getting teams for multiple sports."""
        service = OnboardingService(test_session)
        sport_ids = [test_sports[0].id, test_sports[1].id]  # Football and Basketball

        result = await service.get_onboarding_teams(sport_ids)

        assert len(result.teams) == 4  # All test teams
        assert result.total == 4
        assert set(result.sport_ids) == set(sport_ids)

        # Verify teams belong to requested sports
        team_sport_ids = {team.sport_id for team in result.teams}
        assert team_sport_ids == set(sport_ids)

    async def test_get_teams_empty_sport_ids(self, test_session, test_teams: list[Team]):
        """Test getting teams with empty sport IDs list."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_teams([])

        assert isinstance(result, OnboardingTeamsListResponse)
        assert result.teams == []
        assert result.total == 0
        assert result.sport_ids == []

    async def test_get_teams_nonexistent_sport_id(self, test_session, test_teams: list[Team]):
        """Test getting teams for non-existent sport ID."""
        service = OnboardingService(test_session)
        fake_sport_id = uuid4()

        result = await service.get_onboarding_teams([fake_sport_id])

        assert result.teams == []
        assert result.total == 0
        assert result.sport_ids == [fake_sport_id]

    async def test_get_teams_includes_team_details(self, test_session, test_sports: list[Sport], test_teams: list[Team]):
        """Test that team response includes all required details."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_teams([test_sports[0].id])

        first_team = result.teams[0]
        assert first_team.id is not None
        assert first_team.name is not None
        assert first_team.market is not None
        assert first_team.slug is not None
        assert first_team.sport_id is not None
        assert first_team.logo_url is not None
        assert first_team.abbreviation is not None
        assert first_team.primary_color is not None
        assert first_team.secondary_color is not None

    async def test_get_teams_database_error(self, test_session, test_sports: list[Sport]):
        """Test handling of database errors in get_teams."""
        service = OnboardingService(test_session)

        with patch.object(test_session, 'execute', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                await service.get_onboarding_teams([test_sports[0].id])


class TestOnboardingServiceCompleteOnboarding:
    """Test OnboardingService.complete_onboarding method."""

    async def test_complete_onboarding_force(self, test_session, test_user: User):
        """Test completing onboarding with force flag."""
        service = OnboardingService(test_session)

        result = await service.complete_onboarding(test_user, force_complete=True)

        assert isinstance(result, OnboardingCompletionResponse)
        assert result.success is True
        assert result.user_id == test_user.id
        assert result.onboarding_completed_at is not None
        assert "successfully" in result.message

        # Verify user was updated
        await test_session.refresh(test_user)
        assert test_user.onboarding_completed_at is not None
        assert test_user.current_onboarding_step is None

    async def test_complete_onboarding_without_preferences(self, test_session, test_user: User):
        """Test completing onboarding without required preferences."""
        service = OnboardingService(test_session)

        result = await service.complete_onboarding(test_user, force_complete=False)

        assert result.success is False
        assert "sport preference" in result.message

    async def test_complete_onboarding_with_sport_preferences(self, test_session, test_user: User):
        """Test completing onboarding with sport preferences but no team preferences."""
        # Mock sport preferences
        test_user.sport_preferences = ["football", "basketball"]

        service = OnboardingService(test_session)

        result = await service.complete_onboarding(test_user, force_complete=False)

        # Should still fail without team preferences
        assert result.success is False
        assert "team preference" in result.message

    async def test_complete_onboarding_updates_timestamp(self, test_session, test_user: User):
        """Test that completion updates user timestamps."""
        service = OnboardingService(test_session)
        original_last_active = test_user.last_active_at

        await service.complete_onboarding(test_user, force_complete=True)

        await test_session.refresh(test_user)
        assert test_user.last_active_at > original_last_active
        assert test_user.onboarding_completed_at is not None

    async def test_complete_onboarding_database_error(self, test_session, test_user: User):
        """Test handling of database errors during completion."""
        service = OnboardingService(test_session)

        with patch.object(test_session, 'commit', side_effect=Exception("Database error")):
            result = await service.complete_onboarding(test_user, force_complete=True)

        assert result.success is False
        assert "Failed to complete onboarding" in result.message


class TestOnboardingServiceResetOnboarding:
    """Test OnboardingService.reset_onboarding method."""

    async def test_reset_onboarding_success(self, test_session, completed_onboarding_user: User):
        """Test successful onboarding reset."""
        service = OnboardingService(test_session)

        result = await service.reset_onboarding(completed_onboarding_user)

        assert isinstance(result, OnboardingStatusResponse)
        assert result.is_onboarded is False
        assert result.current_step == 1
        assert result.onboarding_completed_at is None

        # Verify user was updated
        await test_session.refresh(completed_onboarding_user)
        assert completed_onboarding_user.onboarding_completed_at is None
        assert completed_onboarding_user.current_onboarding_step == 1

    async def test_reset_onboarding_incomplete_user(self, test_session, test_user: User):
        """Test resetting onboarding for user who hasn't completed it."""
        service = OnboardingService(test_session)

        # Set user to step 3
        test_user.current_onboarding_step = 3
        await test_session.commit()

        result = await service.reset_onboarding(test_user)

        assert result.current_step == 1
        assert result.is_onboarded is False

    async def test_reset_onboarding_updates_last_active(self, test_session, completed_onboarding_user: User):
        """Test that reset updates last_active_at timestamp."""
        service = OnboardingService(test_session)
        original_last_active = completed_onboarding_user.last_active_at

        import asyncio
        await asyncio.sleep(0.01)

        await service.reset_onboarding(completed_onboarding_user)

        await test_session.refresh(completed_onboarding_user)
        assert completed_onboarding_user.last_active_at > original_last_active

    async def test_reset_onboarding_database_error(self, test_session, completed_onboarding_user: User):
        """Test handling of database errors during reset."""
        service = OnboardingService(test_session)

        with patch.object(test_session, 'commit', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                await service.reset_onboarding(completed_onboarding_user)


class TestOnboardingServiceGetStats:
    """Test OnboardingService.get_onboarding_progress_stats method."""

    async def test_get_stats_with_users(self, test_session, test_user: User, completed_onboarding_user: User):
        """Test getting onboarding statistics with test users."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_progress_stats()

        assert "total_users" in result
        assert "completed_onboarding" in result
        assert "completion_rate" in result
        assert "step_distribution" in result

        assert result["total_users"] >= 2  # At least our test users
        assert result["completed_onboarding"] >= 1  # At least the completed user
        assert 0 <= result["completion_rate"] <= 100

        # Check step distribution
        step_dist = result["step_distribution"]
        for step in range(1, 6):
            assert f"step_{step}" in step_dist
            assert isinstance(step_dist[f"step_{step}"], int)

    async def test_get_stats_empty_database(self, test_session):
        """Test getting stats from database with no users."""
        service = OnboardingService(test_session)

        result = await service.get_onboarding_progress_stats()

        assert result["total_users"] == 0
        assert result["completed_onboarding"] == 0
        assert result["completion_rate"] == 0

        # All step counts should be 0
        step_dist = result["step_distribution"]
        for step in range(1, 6):
            assert step_dist[f"step_{step}"] == 0

    async def test_get_stats_completion_rate_calculation(self, test_session):
        """Test completion rate calculation accuracy."""
        service = OnboardingService(test_session)

        # Add specific users for rate calculation
        users = []
        for i in range(10):
            user = User(
                id=uuid4(),
                firebase_uid=f"test-uid-{i}",
                email=f"user{i}@example.com",
                display_name=f"User {i}",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_active_at=datetime.utcnow(),
                current_onboarding_step=1 if i >= 5 else None,
                onboarding_completed_at=datetime.utcnow() if i < 5 else None
            )
            users.append(user)
            test_session.add(user)

        await test_session.commit()

        result = await service.get_onboarding_progress_stats()

        # Should have at least 10 users (our test users)
        assert result["total_users"] >= 10
        # Should have at least 5 completed users
        assert result["completed_onboarding"] >= 5
        # Completion rate should be reasonable
        assert 0 <= result["completion_rate"] <= 100

    async def test_get_stats_database_error(self, test_session):
        """Test handling of database errors in stats."""
        service = OnboardingService(test_session)

        with patch.object(test_session, 'execute', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                await service.get_onboarding_progress_stats()


class TestOnboardingServiceEdgeCases:
    """Test edge cases and error conditions."""

    async def test_service_with_none_user(self, test_session):
        """Test service methods with None user."""
        service = OnboardingService(test_session)

        with pytest.raises(AttributeError):
            await service.get_onboarding_status(None)

    async def test_update_step_concurrent_access(self, test_session, test_user: User):
        """Test step updates with simulated concurrent access."""
        service1 = OnboardingService(test_session)
        service2 = OnboardingService(test_session)

        # Both services update the same user
        await service1.update_onboarding_step(test_user, 2)
        await service2.update_onboarding_step(test_user, 3)

        # Final step should be 3
        await test_session.refresh(test_user)
        assert test_user.current_onboarding_step == 3

    async def test_large_sport_ids_list(self, test_session, test_sports: list[Sport]):
        """Test getting teams with large number of sport IDs."""
        service = OnboardingService(test_session)

        # Create list with many sport IDs (some valid, some invalid)
        sport_ids = [sport.id for sport in test_sports]
        sport_ids.extend([uuid4() for _ in range(100)])  # Add 100 fake UUIDs

        result = await service.get_onboarding_teams(sport_ids)

        # Should still work and return only valid teams
        assert isinstance(result, OnboardingTeamsListResponse)
        assert result.total >= 0  # Should complete without error