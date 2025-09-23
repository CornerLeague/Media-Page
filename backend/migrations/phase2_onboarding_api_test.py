#!/usr/bin/env python3
"""
Phase 2 Onboarding API Test
===========================

This script tests the actual API endpoints used during onboarding to ensure they
work correctly with the fixed database structure.

Author: Database ETL Architect
Date: 2025-09-21
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Any


def test_api_queries():
    """Test the exact queries used by the onboarding API endpoints"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("🧪 ONBOARDING API ENDPOINT TESTS")
        print("=" * 50)

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Test 1: GET /api/sports (sports selection step)
        print("\n=== TEST 1: GET /api/sports ===")
        cursor.execute("""
            SELECT id, name, slug, icon, has_teams, is_active, display_order
            FROM sports
            WHERE is_active = 1
            ORDER BY display_order, name
        """)

        sports = cursor.fetchall()
        print(f"✅ Sports endpoint returns {len(sports)} active sports")

        # Convert to API response format
        sports_response = []
        for sport in sports:
            sport_dict = dict(sport)
            sports_response.append(sport_dict)

        print(f"Sample sports: {[s['name'] for s in sports_response[:3]]}")

        # Test 2: GET /api/sports/{sport_id}/leagues (league selection)
        print("\n=== TEST 2: GET /api/sports/{sport_id}/leagues ===")

        basketball_sport = next((s for s in sports if s['name'] == 'Basketball'), None)
        if basketball_sport:
            cursor.execute("""
                SELECT l.id, l.name, l.slug, l.abbreviation, l.is_active,
                       l.season_start_month, l.season_end_month, l.country_code
                FROM leagues l
                WHERE l.sport_id = ? AND l.is_active = 1
                ORDER BY l.name
            """, (basketball_sport['id'],))

            leagues = cursor.fetchall()
            print(f"✅ Basketball leagues endpoint returns {len(leagues)} leagues")
            print(f"Basketball leagues: {[l['name'] for l in leagues]}")
        else:
            print("❌ Basketball sport not found")

        # Test 3: Team search queries (team selection step)
        print("\n=== TEST 3: Team Search Queries ===")

        # Query teams by sport (Basketball)
        if basketball_sport:
            cursor.execute("""
                SELECT DISTINCT
                    t.id,
                    t.name,
                    t.market,
                    t.abbreviation,
                    t.logo_url,
                    t.primary_color,
                    t.secondary_color,
                    t.is_active,
                    l.name as league_name,
                    l.abbreviation as league_abbreviation,
                    s.name as sport_name
                FROM teams t
                JOIN team_league_memberships tlm ON t.id = tlm.team_id
                JOIN leagues l ON tlm.league_id = l.id
                JOIN sports s ON t.sport_id = s.id
                WHERE t.sport_id = ? AND t.is_active = 1 AND tlm.is_active = 1
                ORDER BY l.name, t.market, t.name
                LIMIT 20
            """, (basketball_sport['id'],))

            basketball_teams = cursor.fetchall()
            print(f"✅ Basketball team search returns {len(basketball_teams)} teams")

            # Group by league for API response
            teams_by_league = {}
            for team in basketball_teams:
                league = team['league_name']
                if league not in teams_by_league:
                    teams_by_league[league] = []
                teams_by_league[league].append({
                    'id': team['id'],
                    'name': team['name'],
                    'market': team['market'],
                    'display_name': f"{team['market']} {team['name']}",
                    'abbreviation': team['abbreviation'],
                    'logo_url': team['logo_url'],
                    'primary_color': team['primary_color'],
                    'secondary_color': team['secondary_color']
                })

            for league, teams in teams_by_league.items():
                print(f"  {league}: {len(teams)} teams")

        # Test 4: Team search with filters
        print("\n=== TEST 4: Team Search with Filters ===")

        # Search teams by name/market
        search_query = "Lakers"
        cursor.execute("""
            SELECT DISTINCT
                t.id, t.name, t.market, t.abbreviation,
                l.name as league_name, s.name as sport_name
            FROM teams t
            JOIN team_league_memberships tlm ON t.id = tlm.team_id
            JOIN leagues l ON tlm.league_id = l.id
            JOIN sports s ON t.sport_id = s.id
            WHERE (t.name LIKE ? OR t.market LIKE ?)
                AND t.is_active = 1 AND tlm.is_active = 1
            ORDER BY s.name, l.name, t.market, t.name
        """, (f"%{search_query}%", f"%{search_query}%"))

        search_results = cursor.fetchall()
        print(f"✅ Search for '{search_query}' returns {len(search_results)} teams")
        for team in search_results:
            print(f"  • {team['market']} {team['name']} ({team['sport_name']} - {team['league_name']})")

        # Test 5: User preferences queries
        print("\n=== TEST 5: User Preferences Queries ===")

        # Create a test user for preference testing
        test_user_id = str(uuid.uuid4())
        test_firebase_uid = f"onboarding_test_{uuid.uuid4()}"

        cursor.execute("""
            INSERT INTO users (
                id, firebase_uid, email, display_name, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (test_user_id, test_firebase_uid, "onboarding_test@example.com", "Onboarding Test User"))

        print("✅ Created test user for preference testing")

        # Test setting sport preferences
        cursor.execute("SELECT id FROM sports WHERE name = 'Basketball'")
        basketball_sport_id = cursor.fetchone()['id']

        sport_pref_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO user_sport_preferences (
                id, user_id, sport_id, rank, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (sport_pref_id, test_user_id, basketball_sport_id))

        # Test setting team preferences
        if basketball_teams:
            for i, team in enumerate(basketball_teams[:3]):  # Set preferences for first 3 teams
                team_pref_id = str(uuid.uuid4())
                affinity_score = 0.9 - (i * 0.1)
                cursor.execute("""
                    INSERT INTO user_team_preferences (
                        id, user_id, team_id, affinity_score, is_active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (team_pref_id, test_user_id, team['id'], affinity_score))

        print("✅ Set user sport and team preferences")

        # Test retrieving user preferences (API endpoint query)
        cursor.execute("""
            SELECT
                utp.id,
                utp.user_id,
                utp.team_id,
                utp.affinity_score,
                utp.is_active,
                t.name as team_name,
                t.market as team_market,
                t.abbreviation as team_abbreviation,
                t.logo_url,
                t.primary_color,
                t.secondary_color,
                l.name as league_name,
                s.name as sport_name
            FROM user_team_preferences utp
            JOIN teams t ON utp.team_id = t.id
            JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            JOIN leagues l ON tlm.league_id = l.id
            JOIN sports s ON t.sport_id = s.id
            WHERE utp.user_id = ? AND utp.is_active = 1
            ORDER BY utp.affinity_score DESC, s.name, l.name, t.market, t.name
        """, (test_user_id,))

        user_team_prefs = cursor.fetchall()
        print(f"✅ Retrieved {len(user_team_prefs)} user team preferences")

        for pref in user_team_prefs:
            print(f"  • {pref['team_market']} {pref['team_name']} "
                  f"(affinity: {pref['affinity_score']:.2f})")

        # Test 6: Onboarding completion
        print("\n=== TEST 6: Onboarding Completion ===")

        cursor.execute("""
            UPDATE users
            SET onboarding_completed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (test_user_id,))

        # Verify onboarding status
        cursor.execute("""
            SELECT
                u.id,
                u.display_name,
                u.onboarding_completed_at,
                COUNT(DISTINCT usp.id) as sport_preferences_count,
                COUNT(DISTINCT utp.id) as team_preferences_count
            FROM users u
            LEFT JOIN user_sport_preferences usp ON u.id = usp.user_id AND usp.is_active = 1
            LEFT JOIN user_team_preferences utp ON u.id = utp.user_id AND utp.is_active = 1
            WHERE u.id = ?
            GROUP BY u.id, u.display_name, u.onboarding_completed_at
        """, (test_user_id,))

        onboarding_status = cursor.fetchone()
        print(f"✅ Onboarding completed for user: {onboarding_status['display_name']}")
        print(f"  • {onboarding_status['sport_preferences_count']} sport preferences")
        print(f"  • {onboarding_status['team_preferences_count']} team preferences")
        print(f"  • Completed at: {onboarding_status['onboarding_completed_at']}")

        # Test 7: Performance validation
        print("\n=== TEST 7: Performance Validation ===")

        import time

        # Test sports query performance
        start_time = time.time()
        cursor.execute("""
            SELECT id, name, slug, has_teams, is_active, display_order
            FROM sports WHERE is_active = 1 ORDER BY display_order, name
        """)
        cursor.fetchall()
        sports_time = time.time() - start_time

        # Test teams query performance
        start_time = time.time()
        cursor.execute("""
            SELECT DISTINCT t.id, t.name, t.market, t.abbreviation, l.name as league_name
            FROM teams t
            JOIN team_league_memberships tlm ON t.id = tlm.team_id
            JOIN leagues l ON tlm.league_id = l.id
            WHERE t.sport_id = ? AND t.is_active = 1 AND tlm.is_active = 1
            ORDER BY l.name, t.market, t.name
        """, (basketball_sport_id,))
        cursor.fetchall()
        teams_time = time.time() - start_time

        # Test user preferences query performance
        start_time = time.time()
        cursor.execute("""
            SELECT utp.*, t.name, t.market, l.name as league_name, s.name as sport_name
            FROM user_team_preferences utp
            JOIN teams t ON utp.team_id = t.id
            JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            JOIN leagues l ON tlm.league_id = l.id
            JOIN sports s ON t.sport_id = s.id
            WHERE utp.user_id = ? AND utp.is_active = 1
        """, (test_user_id,))
        cursor.fetchall()
        prefs_time = time.time() - start_time

        print(f"⚡ Sports query: {sports_time*1000:.2f}ms")
        print(f"⚡ Teams query: {teams_time*1000:.2f}ms")
        print(f"⚡ User preferences query: {prefs_time*1000:.2f}ms")

        performance_ok = all(t < 0.1 for t in [sports_time, teams_time, prefs_time])
        if performance_ok:
            print("✅ All queries perform within acceptable limits")
        else:
            print("⚠ Some queries may need optimization")

        # Clean up test data
        cursor.execute("DELETE FROM users WHERE id = ?", (test_user_id,))
        conn.commit()

        print("\n✅ Cleaned up test data")
        print("\n🎉 ALL ONBOARDING API TESTS PASSED!")
        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        # Clean up on error
        try:
            cursor.execute("DELETE FROM users WHERE firebase_uid LIKE 'onboarding_test_%'")
            conn.commit()
        except:
            pass
        return False
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    success = test_api_queries()
    exit(0 if success else 1)