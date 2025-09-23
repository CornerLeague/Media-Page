#!/usr/bin/env python3
"""
Test script for Phase 4 API functionality
=========================================

This script tests the key API endpoints to ensure they work correctly
after the Phase 4 schema cleanup that removed the league_id column.
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add the backend directory to the path
sys.path.insert(0, '/Users/newmac/Desktop/Corner League Media 1/backend')

from database import get_async_session
from api.services.sports_service import SportsService
from api.schemas.sports import SoccerTeamFilters
from models.sports import Team, League, TeamLeagueMembership


async def test_database_connection():
    """Test basic database connectivity"""
    print("=== Testing Database Connection ===")

    async for db_session in get_async_session():
        try:
            # Test basic team query
            result = await db_session.execute(
                select(Team).limit(1)
            )
            team = result.scalar_one_or_none()

            if team:
                print(f"✓ Database connection successful")
                print(f"  Sample team: {team.market} {team.name}")
            else:
                print("✗ No teams found in database")
                return False

        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    return True


async def test_sports_service():
    """Test the updated sports service functionality"""
    print("\n=== Testing Sports Service ===")

    async for db_session in get_async_session():
        service = SportsService(db_session)

        try:
            # Test 1: Get soccer sport ID
            soccer_sport_id = await service.get_soccer_sport_id()
            if soccer_sport_id:
                print(f"✓ Soccer sport ID: {soccer_sport_id}")
            else:
                print("✗ Could not find soccer sport")
                return False

            # Test 2: Get teams with multi-league info
            filters = SoccerTeamFilters(page=1, page_size=5)
            teams, total_count = await service.get_teams_with_multi_league_info(filters)

            print(f"✓ Retrieved {len(teams)} teams (total: {total_count})")

            if teams:
                sample_team = teams[0]
                print(f"  Sample team: {sample_team.display_name}")
                print(f"  Primary league: {sample_team.primary_league.name if sample_team.primary_league else 'None'}")
                print(f"  Total leagues: {len(sample_team.all_leagues)}")
                print(f"  Is multi-league: {sample_team.is_multi_league}")

            # Test 3: Get multi-league teams specifically
            multi_league_teams = await service.get_multi_league_teams()
            print(f"✓ Found {len(multi_league_teams)} multi-league teams")

            if multi_league_teams:
                sample_multi = multi_league_teams[0]
                print(f"  Sample multi-league team: {sample_multi.display_name}")
                league_names = [league.name for league in sample_multi.all_leagues]
                print(f"  Leagues: {', '.join(league_names)}")

            # Test 4: Get leagues with team counts
            leagues_with_counts = await service.get_soccer_leagues_with_team_counts()
            print(f"✓ Found {len(leagues_with_counts)} leagues with team counts")

            if leagues_with_counts:
                sample_league = leagues_with_counts[0]
                print(f"  Sample league: {sample_league['name']} ({sample_league['current_teams']} teams)")

        except Exception as e:
            print(f"✗ Sports service test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    return True


async def test_team_league_queries():
    """Test specific team-league relationship queries"""
    print("\n=== Testing Team-League Queries ===")

    async for db_session in get_async_session():
        service = SportsService(db_session)

        try:
            # Get a sample team with leagues
            filters = SoccerTeamFilters(page=1, page_size=1)
            teams, _ = await service.get_teams_with_multi_league_info(filters)

            if not teams:
                print("✗ No teams found for testing")
                return False

            sample_team = teams[0]
            print(f"Testing with team: {sample_team.display_name} (ID: {sample_team.id})")

            # Test get team leagues
            team_leagues = await service.get_team_leagues(sample_team.id)
            print(f"✓ Team has {len(team_leagues)} league memberships")

            for league in team_leagues:
                primary_marker = " (PRIMARY)" if league.is_primary else ""
                print(f"  - {league.name} ({league.competition_type}){primary_marker}")

            # Test get league teams (use the first league)
            if team_leagues:
                first_league = team_leagues[0]
                league_teams = await service.get_league_teams(first_league.id)
                print(f"✓ League '{first_league.name}' has {len(league_teams)} teams")

                # Show a few team names
                for i, team in enumerate(league_teams[:3]):
                    print(f"  - {team.display_name}")
                if len(league_teams) > 3:
                    print(f"  ... and {len(league_teams) - 3} more")

        except Exception as e:
            print(f"✗ Team-league query test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    return True


async def test_primary_league_logic():
    """Test the new primary league determination logic"""
    print("\n=== Testing Primary League Logic ===")

    async for db_session in get_async_session():
        service = SportsService(db_session)

        try:
            # Find a multi-league team to test with
            multi_league_teams = await service.get_multi_league_teams()

            if not multi_league_teams:
                print("⚠ No multi-league teams found for testing")
                return True

            sample_team = multi_league_teams[0]
            print(f"Testing primary league logic with: {sample_team.display_name}")

            # Check the primary league determination
            primary_league = sample_team.primary_league
            all_leagues = sample_team.all_leagues

            print(f"✓ Primary league: {primary_league.name if primary_league else 'None'}")
            print(f"✓ All leagues ({len(all_leagues)}):")

            for league in all_leagues:
                primary_marker = " (PRIMARY)" if league.is_primary else ""
                print(f"  - {league.name} (Level {league.league_level}, {league.competition_type}){primary_marker}")

            # Verify only one league is marked as primary
            primary_count = sum(1 for league in all_leagues if league.is_primary)
            if primary_count == 1:
                print("✓ Exactly one league marked as primary")
            else:
                print(f"✗ Expected 1 primary league, found {primary_count}")
                return False

        except Exception as e:
            print(f"✗ Primary league logic test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    return True


async def run_all_tests():
    """Run all Phase 4 API tests"""
    print("🧪 PHASE 4 API FUNCTIONALITY TESTS")
    print("=" * 50)

    tests = [
        test_database_connection,
        test_sports_service,
        test_team_league_queries,
        test_primary_league_logic
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)

    print(f"\n=== TEST RESULTS ===")
    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 4 API is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Phase 4 API needs attention.")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)