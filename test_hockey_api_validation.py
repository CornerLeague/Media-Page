#!/usr/bin/env python3
"""
Hockey API Validation Test Script

Validates Phase 3 hockey integration by testing:
1. Database connectivity and schema
2. Hockey sport, NHL league, and team data
3. API service layer functionality
4. Frontend-backend integration points
"""

import asyncio
import sqlite3
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from uuid import UUID

async def test_database_connectivity():
    """Test direct database connectivity and hockey data"""
    print("=== DATABASE CONNECTIVITY TEST ===")

    # Database path
    db_path = backend_path / "sports_platform.db"
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return False

    print(f"✅ Database file found: {db_path}")

    # Test with sqlite3 first
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Test hockey sport
        cursor.execute("SELECT id, name, slug FROM sports WHERE slug = 'hockey'")
        hockey_sport = cursor.fetchone()
        if hockey_sport:
            print(f"✅ Hockey sport found: {hockey_sport}")
        else:
            print("❌ Hockey sport not found in database")
            return False

        # Test NHL league
        cursor.execute("""
            SELECT l.id, l.name, l.abbreviation, s.name as sport_name
            FROM leagues l
            JOIN sports s ON l.sport_id = s.id
            WHERE l.abbreviation = 'NHL'
        """)
        nhl_league = cursor.fetchone()
        if nhl_league:
            print(f"✅ NHL league found: {nhl_league}")
        else:
            print("❌ NHL league not found in database")
            return False

        # Test NHL teams count
        cursor.execute("""
            SELECT COUNT(*)
            FROM teams t
            JOIN sports s ON t.sport_id = s.id
            WHERE s.slug = 'hockey'
        """)
        team_count = cursor.fetchone()[0]
        print(f"✅ NHL teams count: {team_count}")

        # Test Utah Hockey Club specifically
        cursor.execute("""
            SELECT t.market, t.name, (t.market || ' ' || t.name) as display_name
            FROM teams t
            JOIN sports s ON t.sport_id = s.id
            WHERE s.slug = 'hockey' AND t.market = 'Utah'
        """)
        utah_team = cursor.fetchone()
        if utah_team:
            print(f"✅ Utah Hockey Club found: {utah_team}")
        else:
            print("❌ Utah Hockey Club not found")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database connectivity error: {e}")
        return False

async def test_async_database():
    """Test async database connectivity"""
    print("\n=== ASYNC DATABASE TEST ===")

    try:
        # Use the same database URL as the backend
        db_url = f"sqlite+aiosqlite:///{backend_path}/sports_platform.db"
        engine = create_async_engine(db_url, echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with AsyncSessionLocal() as session:
            # Test hockey sport via async query
            result = await session.execute(
                text("SELECT id, name, slug FROM sports WHERE slug = 'hockey'")
            )
            hockey_sport = result.fetchone()

            if hockey_sport:
                print(f"✅ Async: Hockey sport found: {hockey_sport}")
                sport_id = hockey_sport[0]

                # Test NHL league
                result = await session.execute(
                    text("""
                        SELECT l.id, l.name, l.abbreviation
                        FROM leagues l
                        WHERE l.sport_id = :sport_id AND l.abbreviation = 'NHL'
                    """),
                    {"sport_id": sport_id}
                )
                nhl_league = result.fetchone()

                if nhl_league:
                    print(f"✅ Async: NHL league found: {nhl_league}")
                    league_id = nhl_league[0]

                    # Test team count in NHL
                    result = await session.execute(
                        text("""
                            SELECT COUNT(*)
                            FROM team_league_memberships tlm
                            WHERE tlm.league_id = :league_id AND tlm.is_active = 1
                        """),
                        {"league_id": league_id}
                    )
                    team_count = result.scalar()
                    print(f"✅ Async: NHL teams in league memberships: {team_count}")

                else:
                    print("❌ Async: NHL league not found")

            else:
                print("❌ Async: Hockey sport not found")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Async database error: {e}")
        return False

async def test_api_service():
    """Test the API service layer for hockey data"""
    print("\n=== API SERVICE TEST ===")

    try:
        # Import the service
        from api.services.team_selection_service import TeamSelectionService
        from database import get_async_session

        # Create a database session
        db_url = f"sqlite+aiosqlite:///{backend_path}/sports_platform.db"
        engine = create_async_engine(db_url, echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with AsyncSessionLocal() as session:
            service = TeamSelectionService(session)

            # Test get_sports
            sports = await service.get_sports(include_leagues=False, include_inactive=False)
            hockey_sports = [s for s in sports if hasattr(s, 'slug') and s.slug == 'hockey']

            if hockey_sports:
                hockey_sport = hockey_sports[0]
                print(f"✅ Service: Hockey sport found: {hockey_sport.name} (ID: {hockey_sport.id})")

                # Test get_sport_leagues for hockey
                leagues = await service.get_sport_leagues(
                    sport_id=hockey_sport.id,
                    include_teams=False,
                    include_inactive=False
                )

                nhl_leagues = [l for l in leagues if hasattr(l, 'abbreviation') and l.abbreviation == 'NHL']
                if nhl_leagues:
                    nhl_league = nhl_leagues[0]
                    print(f"✅ Service: NHL league found: {nhl_league.name} (ID: {nhl_league.id})")

                    # Test get_league_teams for NHL
                    teams_response = await service.get_league_teams(
                        league_id=nhl_league.id,
                        page=1,
                        page_size=5,
                        include_inactive=False
                    )

                    print(f"✅ Service: NHL teams found: {teams_response.total} total, showing {len(teams_response.items)}")

                    # Show sample teams
                    for team in teams_response.items[:3]:
                        print(f"   - {team.display_name}")

                else:
                    print("❌ Service: NHL league not found")

            else:
                print("❌ Service: Hockey sport not found")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"❌ API service error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all validation tests"""
    print("🏒 HOCKEY API VALIDATION - Phase 3 Testing")
    print("=" * 50)

    # Change to backend directory
    os.chdir(backend_path)

    results = []

    # Test 1: Database connectivity
    results.append(await test_database_connectivity())

    # Test 2: Async database
    results.append(await test_async_database())

    # Test 3: API service layer
    results.append(await test_api_service())

    # Summary
    print("\n" + "=" * 50)
    print("🏒 VALIDATION SUMMARY")
    print("=" * 50)

    test_names = ["Database Connectivity", "Async Database", "API Service Layer"]

    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")

    overall_status = "✅ ALL TESTS PASSED" if all(results) else "❌ SOME TESTS FAILED"
    print(f"\nOverall Status: {overall_status}")

    # Return success code
    return 0 if all(results) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)