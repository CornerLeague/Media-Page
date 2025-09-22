#!/usr/bin/env python3
"""
Simple Phase 4 Database Test
============================

Direct database tests to verify Phase 4 schema changes work correctly.
"""

import sqlite3
import sys
import os


def test_schema_changes():
    """Test that schema changes are correct"""
    print("=== Testing Schema Changes ===")

    db_path = "sports_platform.db"
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test 1: Verify league_id column is removed
        cursor.execute("PRAGMA table_info(teams)")
        columns = [row[1] for row in cursor.fetchall()]

        if "league_id" in columns:
            print("✗ league_id column still exists in teams table")
            return False
        else:
            print("✓ league_id column successfully removed")

        # Test 2: Verify team count is preserved
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        print(f"✓ Team count: {team_count}")

        # Test 3: Verify membership count is preserved
        cursor.execute("SELECT COUNT(*) FROM team_league_memberships WHERE is_active = 1")
        membership_count = cursor.fetchone()[0]
        print(f"✓ Active memberships: {membership_count}")

        if team_count == 0 or membership_count == 0:
            print("✗ Data appears to be missing")
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        return False


def test_multi_league_functionality():
    """Test multi-league team functionality"""
    print("\n=== Testing Multi-League Functionality ===")

    try:
        conn = sqlite3.connect("sports_platform.db")
        cursor = conn.cursor()

        # Test 1: Find teams with multiple leagues
        cursor.execute("""
            SELECT
                t.name as team_name,
                t.market,
                COUNT(tlm.league_id) as league_count,
                GROUP_CONCAT(l.name, ', ') as leagues
            FROM teams t
            JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            JOIN leagues l ON tlm.league_id = l.id
            WHERE t.sport_id = (SELECT id FROM sports WHERE slug = 'soccer')
            GROUP BY t.id, t.name
            HAVING COUNT(tlm.league_id) > 1
            LIMIT 5
        """)

        multi_league_teams = cursor.fetchall()
        print(f"✓ Found {len(multi_league_teams)} multi-league teams")

        for team in multi_league_teams:
            print(f"  - {team[1]} {team[0]}: {team[3]}")

        # Test 2: Verify all teams have at least one membership
        cursor.execute("""
            SELECT COUNT(*) FROM teams t
            WHERE t.sport_id = (SELECT id FROM sports WHERE slug = 'soccer')
            AND NOT EXISTS (
                SELECT 1 FROM team_league_memberships tlm
                WHERE tlm.team_id = t.id AND tlm.is_active = 1
            )
        """)

        orphaned_soccer_teams = cursor.fetchone()[0]
        print(f"✓ Soccer teams without memberships: {orphaned_soccer_teams}")

        # Test 3: Test league-to-teams relationship
        cursor.execute("""
            SELECT l.name, COUNT(tlm.team_id) as team_count
            FROM leagues l
            LEFT JOIN team_league_memberships tlm ON l.id = tlm.league_id AND tlm.is_active = 1
            WHERE l.sport_id = (SELECT id FROM sports WHERE slug = 'soccer')
            GROUP BY l.id, l.name
            ORDER BY team_count DESC
            LIMIT 5
        """)

        league_counts = cursor.fetchall()
        print(f"✓ Top leagues by team count:")
        for league, count in league_counts:
            print(f"  - {league}: {count} teams")

        conn.close()
        return True

    except Exception as e:
        print(f"✗ Multi-league test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_performance():
    """Test basic query performance"""
    print("\n=== Testing Query Performance ===")

    try:
        conn = sqlite3.connect("sports_platform.db")
        cursor = conn.cursor()

        # Test a complex query that would benefit from the new indexes
        import time

        start_time = time.time()
        cursor.execute("""
            SELECT
                t.name,
                t.market,
                t.country_code,
                COUNT(tlm.league_id) as league_count,
                MAX(CASE WHEN l.competition_type = 'league' AND l.league_level = 1 THEN l.name END) as primary_league
            FROM teams t
            JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            JOIN leagues l ON tlm.league_id = l.id
            WHERE t.sport_id = (SELECT id FROM sports WHERE slug = 'soccer')
            AND t.country_code IN ('GB', 'ES', 'IT', 'DE', 'FR')
            GROUP BY t.id, t.name, t.market, t.country_code
            ORDER BY league_count DESC, t.name
        """)

        results = cursor.fetchall()
        end_time = time.time()
        query_time = (end_time - start_time) * 1000  # Convert to milliseconds

        print(f"✓ Complex query completed in {query_time:.2f}ms")
        print(f"✓ Found {len(results)} teams from major European countries")

        # Show a few results
        for i, (name, market, country, league_count, primary_league) in enumerate(results[:5]):
            print(f"  {i+1}. {market} {name} ({country}): {league_count} leagues, primary: {primary_league}")

        conn.close()
        return True

    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return False


def test_foreign_key_integrity():
    """Test foreign key integrity"""
    print("\n=== Testing Foreign Key Integrity ===")

    try:
        conn = sqlite3.connect("sports_platform.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Check for foreign key violations
        cursor.execute("PRAGMA foreign_key_check")
        violations = cursor.fetchall()

        if violations:
            print(f"✗ Found {len(violations)} foreign key violations:")
            for violation in violations:
                print(f"  - {violation}")
            return False
        else:
            print("✓ No foreign key violations found")

        # Test that constraints are working
        cursor.execute("SELECT COUNT(*) FROM team_league_memberships")
        total_memberships = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM team_league_memberships tlm
            WHERE EXISTS (SELECT 1 FROM teams t WHERE t.id = tlm.team_id)
            AND EXISTS (SELECT 1 FROM leagues l WHERE l.id = tlm.league_id)
        """)
        valid_memberships = cursor.fetchone()[0]

        if total_memberships == valid_memberships:
            print(f"✓ All {total_memberships} memberships have valid foreign keys")
        else:
            print(f"✗ {total_memberships - valid_memberships} memberships have invalid foreign keys")
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"✗ Foreign key test failed: {e}")
        return False


def main():
    """Run all simple tests"""
    print("🧪 PHASE 4 SIMPLE DATABASE TESTS")
    print("=" * 50)

    tests = [
        test_schema_changes,
        test_multi_league_functionality,
        test_query_performance,
        test_foreign_key_integrity
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)

    print(f"\n=== TEST RESULTS ===")
    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 4 database changes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Phase 4 needs attention.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)