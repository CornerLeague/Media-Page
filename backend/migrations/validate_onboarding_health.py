#!/usr/bin/env python3
"""
Onboarding Health Validation Script
==================================

Quick health check script to validate the onboarding system is working correctly.
Run this script anytime to verify database integrity for onboarding flow.

Usage:
    python validate_onboarding_health.py

Author: Database ETL Architect
Date: 2025-09-21
"""

import sqlite3
import sys
from datetime import datetime


def main():
    """Run comprehensive onboarding health check"""

    print("🏥 ONBOARDING HEALTH CHECK")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Health checks
        checks = [
            check_orphaned_teams,
            check_user_tables,
            check_sports_coverage,
            check_query_performance,
            check_foreign_keys
        ]

        results = []
        for check in checks:
            try:
                result = check(cursor)
                results.append(result)
            except Exception as e:
                results.append({
                    'name': check.__name__.replace('check_', '').replace('_', ' ').title(),
                    'status': False,
                    'message': f"Error: {e}"
                })

        # Summary
        print("\n" + "=" * 40)
        print("HEALTH CHECK SUMMARY")
        print("=" * 40)

        passed = sum(1 for r in results if r['status'])
        total = len(results)

        for result in results:
            status_icon = "✅" if result['status'] else "❌"
            print(f"{status_icon} {result['name']}: {result['message']}")

        print(f"\nOverall: {passed}/{total} checks passed")

        if passed == total:
            print("🎉 ONBOARDING SYSTEM HEALTHY!")
            return True
        else:
            print("⚠ ONBOARDING SYSTEM NEEDS ATTENTION")
            return False

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def check_orphaned_teams(cursor):
    """Check for teams without league memberships"""
    cursor.execute("""
        SELECT COUNT(*) as count FROM teams t
        LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
        WHERE tlm.team_id IS NULL AND t.is_active = 1
    """)

    orphaned_count = cursor.fetchone()['count']

    return {
        'name': 'Orphaned Teams',
        'status': orphaned_count == 0,
        'message': f"{orphaned_count} orphaned teams" if orphaned_count > 0 else "No orphaned teams"
    }


def check_user_tables(cursor):
    """Check that all user preference tables exist"""
    required_tables = [
        'users',
        'user_sport_preferences',
        'user_team_preferences',
        'user_news_preferences',
        'user_notification_settings'
    ]

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ({})
    """.format(','.join('?' * len(required_tables))), required_tables)

    existing_tables = [row['name'] for row in cursor.fetchall()]
    missing_tables = [table for table in required_tables if table not in existing_tables]

    return {
        'name': 'User Preference Tables',
        'status': len(missing_tables) == 0,
        'message': f"Missing: {missing_tables}" if missing_tables else "All tables exist"
    }


def check_sports_coverage(cursor):
    """Check that priority sports have teams available"""
    priority_sports = ['Basketball', 'Football', 'College Football', 'Baseball', 'Soccer']

    problems = []

    for sport_name in priority_sports:
        cursor.execute("""
            SELECT COUNT(DISTINCT t.id) as team_count
            FROM sports s
            LEFT JOIN teams t ON s.id = t.sport_id AND t.is_active = 1
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            WHERE s.name = ? AND tlm.team_id IS NOT NULL
        """, (sport_name,))

        result = cursor.fetchone()
        team_count = result['team_count'] if result else 0

        if team_count == 0:
            problems.append(f"{sport_name}: 0 teams")

    return {
        'name': 'Sports Coverage',
        'status': len(problems) == 0,
        'message': f"Issues: {problems}" if problems else "All priority sports have teams"
    }


def check_query_performance(cursor):
    """Check that key queries perform well"""
    import time

    # Test sports query
    start = time.time()
    cursor.execute("SELECT id, name FROM sports WHERE is_active = 1")
    cursor.fetchall()
    sports_time = time.time() - start

    # Test teams query
    start = time.time()
    cursor.execute("""
        SELECT DISTINCT t.id, t.name, t.market
        FROM teams t
        JOIN team_league_memberships tlm ON t.id = tlm.team_id
        WHERE t.is_active = 1 AND tlm.is_active = 1
        LIMIT 50
    """)
    cursor.fetchall()
    teams_time = time.time() - start

    max_time = max(sports_time, teams_time)

    return {
        'name': 'Query Performance',
        'status': max_time < 0.1,  # Under 100ms
        'message': f"Max query time: {max_time*1000:.1f}ms" + (" (slow)" if max_time >= 0.1 else "")
    }


def check_foreign_keys(cursor):
    """Check foreign key integrity"""

    # Check teams without sports
    cursor.execute("""
        SELECT COUNT(*) as count FROM teams t
        LEFT JOIN sports s ON t.sport_id = s.id
        WHERE s.id IS NULL
    """)
    teams_without_sports = cursor.fetchone()['count']

    # Check memberships with invalid references
    cursor.execute("""
        SELECT COUNT(*) as count FROM team_league_memberships tlm
        LEFT JOIN teams t ON tlm.team_id = t.id
        LEFT JOIN leagues l ON tlm.league_id = l.id
        WHERE t.id IS NULL OR l.id IS NULL
    """)
    invalid_memberships = cursor.fetchone()['count']

    total_violations = teams_without_sports + invalid_memberships

    return {
        'name': 'Foreign Key Integrity',
        'status': total_violations == 0,
        'message': f"{total_violations} violations" if total_violations > 0 else "All foreign keys valid"
    }


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)