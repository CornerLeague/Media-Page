#!/usr/bin/env python3
"""
Phase 2 Onboarding API Validation
==================================

This script validates that the database can properly support onboarding API queries.
It simulates the exact queries that the onboarding flow uses to ensure teams can
be retrieved and displayed correctly.

Author: Database ETL Architect
Date: 2025-09-21
"""

import sqlite3
import json
from typing import Dict, List, Any


def validate_onboarding_queries():
    """Validate queries used by the onboarding API endpoints"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("🔍 ONBOARDING API VALIDATION")
        print("=" * 50)

        # 1. Test sports selection query (first step of onboarding)
        print("\n=== 1. SPORTS SELECTION QUERY ===")
        cursor.execute("""
            SELECT id, name, slug, icon, has_teams, is_active, display_order
            FROM sports
            WHERE is_active = 1
            ORDER BY display_order, name
        """)

        sports = cursor.fetchall()
        print(f"✅ Found {len(sports)} active sports for selection:")
        for sport in sports:
            print(f"  • {sport['name']} (teams: {sport['has_teams']}, order: {sport['display_order']})")

        # 2. Test teams by sport query (team selection step)
        print("\n=== 2. TEAMS BY SPORT QUERIES ===")

        priority_sports = ["Basketball", "Football", "College Football", "Baseball", "Soccer"]

        for sport_name in priority_sports:
            print(f"\n--- {sport_name} Teams ---")

            # Get sport ID
            cursor.execute("SELECT id FROM sports WHERE name = ?", (sport_name,))
            sport_result = cursor.fetchone()

            if not sport_result:
                print(f"❌ Sport '{sport_name}' not found")
                continue

            sport_id = sport_result['id']

            # Query teams with league info (mimics API response)
            cursor.execute("""
                SELECT DISTINCT
                    t.id,
                    t.name,
                    t.market,
                    t.abbreviation,
                    t.logo_url,
                    t.primary_color,
                    t.secondary_color,
                    l.name as league_name,
                    l.abbreviation as league_abbreviation
                FROM teams t
                JOIN team_league_memberships tlm ON t.id = tlm.team_id
                JOIN leagues l ON tlm.league_id = l.id
                WHERE t.sport_id = ? AND t.is_active = 1 AND tlm.is_active = 1
                ORDER BY l.name, t.market, t.name
            """, (sport_id,))

            teams = cursor.fetchall()

            if teams:
                print(f"✅ Found {len(teams)} teams available for selection")

                # Group by league for display
                league_groups = {}
                for team in teams:
                    league = team['league_name'] or team['league_abbreviation'] or 'Unknown'
                    if league not in league_groups:
                        league_groups[league] = []
                    league_groups[league].append(team)

                for league, league_teams in league_groups.items():
                    print(f"  📂 {league}: {len(league_teams)} teams")
                    for team in league_teams[:3]:  # Show first 3 teams
                        display_name = f"{team['market']} {team['name']}"
                        abbr = f" ({team['abbreviation']})" if team['abbreviation'] else ""
                        print(f"    • {display_name}{abbr}")
                    if len(league_teams) > 3:
                        print(f"    ... and {len(league_teams) - 3} more")
            else:
                print(f"❌ No teams found for {sport_name}")

        # 3. Test specific team lookup query (for team details)
        print("\n=== 3. TEAM DETAILS QUERY VALIDATION ===")

        # Test getting full team details for a random team
        cursor.execute("""
            SELECT t.*, s.name as sport_name,
                   l.name as primary_league_name,
                   l.abbreviation as primary_league_abbr
            FROM teams t
            JOIN sports s ON t.sport_id = s.id
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            LEFT JOIN leagues l ON tlm.league_id = l.id
            WHERE t.is_active = 1
            LIMIT 5
        """)

        sample_teams = cursor.fetchall()
        print(f"✅ Sample team details queries working ({len(sample_teams)} tested)")

        for team in sample_teams:
            print(f"  • {team['market']} {team['name']} ({team['sport_name']} - {team['primary_league_name']})")

        # 4. Test user preference storage query
        print("\n=== 4. USER PREFERENCE STORAGE VALIDATION ===")

        # Check if user_team_preferences table exists and is properly structured
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='user_team_preferences'
        """)

        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(user_team_preferences)")
            columns = cursor.fetchall()
            print("✅ User team preferences table exists with columns:")
            for col in columns:
                print(f"  • {col['name']} ({col['type']})")

            # Test constraint validation
            cursor.execute("""
                SELECT COUNT(*) as count FROM user_team_preferences utp
                LEFT JOIN teams t ON utp.team_id = t.id
                WHERE t.id IS NULL
            """)
            orphaned_prefs = cursor.fetchone()['count']

            if orphaned_prefs == 0:
                print("✅ No orphaned user preferences")
            else:
                print(f"❌ {orphaned_prefs} user preferences reference non-existent teams")
        else:
            print("⚠ User team preferences table not found (may be created later)")

        # 5. Test performance of onboarding queries
        print("\n=== 5. QUERY PERFORMANCE VALIDATION ===")

        import time

        # Test sports query performance
        start_time = time.time()
        cursor.execute("""
            SELECT id, name, slug, icon, has_teams, is_active
            FROM sports WHERE is_active = 1 ORDER BY display_order, name
        """)
        cursor.fetchall()
        sports_time = time.time() - start_time

        # Test teams query performance (for Basketball)
        start_time = time.time()
        cursor.execute("""
            SELECT DISTINCT t.id, t.name, t.market, t.abbreviation, l.name as league_name
            FROM teams t
            JOIN team_league_memberships tlm ON t.id = tlm.team_id
            JOIN leagues l ON tlm.league_id = l.id
            JOIN sports s ON t.sport_id = s.id
            WHERE s.name = 'Basketball' AND t.is_active = 1 AND tlm.is_active = 1
            ORDER BY l.name, t.market, t.name
        """)
        cursor.fetchall()
        teams_time = time.time() - start_time

        print(f"⚡ Sports query: {sports_time*1000:.2f}ms")
        print(f"⚡ Teams query: {teams_time*1000:.2f}ms")

        if sports_time < 0.1 and teams_time < 0.1:
            print("✅ Query performance is acceptable for onboarding")
        else:
            print("⚠ Query performance may need optimization")

        # 6. Final validation summary
        print("\n=== 6. ONBOARDING READINESS SUMMARY ===")

        readiness_checks = []

        # Check 1: All priority sports have teams
        for sport_name in priority_sports:
            cursor.execute("""
                SELECT COUNT(DISTINCT t.id) as team_count
                FROM sports s
                JOIN teams t ON s.id = t.sport_id
                JOIN team_league_memberships tlm ON t.id = tlm.team_id
                WHERE s.name = ? AND t.is_active = 1 AND tlm.is_active = 1
            """, (sport_name,))

            count = cursor.fetchone()['team_count']
            readiness_checks.append((f"{sport_name} teams available", count > 0, count))

        # Check 2: No orphaned teams
        cursor.execute("""
            SELECT COUNT(*) as count FROM teams t
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            WHERE tlm.team_id IS NULL AND t.is_active = 1
        """)
        no_orphans = cursor.fetchone()['count'] == 0
        readiness_checks.append(("No orphaned teams", no_orphans, 0 if no_orphans else 1))

        # Check 3: Foreign key integrity
        cursor.execute("""
            SELECT COUNT(*) as count FROM team_league_memberships tlm
            LEFT JOIN teams t ON tlm.team_id = t.id
            LEFT JOIN leagues l ON tlm.league_id = l.id
            WHERE t.id IS NULL OR l.id IS NULL
        """)
        integrity_ok = cursor.fetchone()['count'] == 0
        readiness_checks.append(("Foreign key integrity", integrity_ok, 0 if integrity_ok else 1))

        # Print results
        all_passed = True
        for check_name, passed, details in readiness_checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False

        if all_passed:
            print("\n🎉 DATABASE IS READY FOR ONBOARDING!")
            print("   • All sports have teams with proper league memberships")
            print("   • API queries will return valid data")
            print("   • No blocking issues detected")
            return True
        else:
            print("\n❌ ONBOARDING READINESS ISSUES DETECTED")
            print("   • Review failed checks above")
            print("   • Run repair scripts if needed")
            return False

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    success = validate_onboarding_queries()
    exit(0 if success else 1)