#!/usr/bin/env python3
"""
Phase 2 Critical Database Analysis
==================================

This script performs comprehensive analysis of the sports database to identify:
1. Orphaned teams (teams without league memberships)
2. Broken foreign key relationships
3. Referential integrity issues
4. Data quality problems affecting onboarding

Author: Database ETL Architect
Date: 2025-09-21
"""

import sqlite3
import sys
from typing import Dict, List, Tuple


def analyze_database_integrity():
    """Analyze database for critical issues affecting onboarding"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("🔍 PHASE 2 CRITICAL DATABASE ANALYSIS")
        print("=" * 60)

        # 1. Check orphaned teams (teams without league memberships)
        print("\n=== 1. ORPHANED TEAMS ANALYSIS ===")
        cursor.execute("""
            SELECT t.id, t.name, t.market, s.name as sport, t.is_active
            FROM teams t
            JOIN sports s ON t.sport_id = s.id
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            WHERE tlm.team_id IS NULL AND t.is_active = 1
            ORDER BY s.name, t.market, t.name
        """)

        orphaned_teams = cursor.fetchall()
        if orphaned_teams:
            print(f"❌ CRITICAL: Found {len(orphaned_teams)} orphaned teams!")
            for team in orphaned_teams:
                print(f"  • {team['sport']}: {team['market']} {team['name']} (ID: {team['id'][:8]}...)")
        else:
            print("✅ No orphaned teams found")

        # 2. Check teams by sport
        print("\n=== 2. TEAMS BY SPORT ANALYSIS ===")
        cursor.execute("""
            SELECT s.name as sport,
                   COUNT(DISTINCT t.id) as total_teams,
                   COUNT(DISTINCT CASE WHEN tlm.team_id IS NOT NULL THEN t.id END) as teams_with_leagues,
                   COUNT(DISTINCT CASE WHEN tlm.team_id IS NULL THEN t.id END) as teams_without_leagues
            FROM sports s
            LEFT JOIN teams t ON s.id = t.sport_id AND t.is_active = 1
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            GROUP BY s.id, s.name
            ORDER BY s.name
        """)

        sport_stats = cursor.fetchall()
        for stat in sport_stats:
            status = "❌" if stat['teams_without_leagues'] > 0 else "✅"
            print(f"{status} {stat['sport']:<20} Total: {stat['total_teams']:>3}, "
                  f"With Leagues: {stat['teams_with_leagues']:>3}, "
                  f"Without: {stat['teams_without_leagues']:>3}")

        # 3. Check league coverage
        print("\n=== 3. LEAGUE COVERAGE ANALYSIS ===")
        cursor.execute("""
            SELECT s.name as sport, l.name as league,
                   COUNT(tlm.team_id) as team_count,
                   l.is_active
            FROM sports s
            LEFT JOIN leagues l ON s.id = l.sport_id
            LEFT JOIN team_league_memberships tlm ON l.id = tlm.league_id AND tlm.is_active = 1
            GROUP BY s.id, s.name, l.id, l.name, l.is_active
            ORDER BY s.name, l.name
        """)

        league_coverage = cursor.fetchall()
        current_sport = None
        for coverage in league_coverage:
            if coverage['sport'] != current_sport:
                current_sport = coverage['sport']
                print(f"\n{current_sport}:")

            if coverage['league']:
                status = "✅" if coverage['is_active'] else "⚠"
                print(f"  {status} {coverage['league']:<30} {coverage['team_count']:>3} teams")
            else:
                print(f"  ❌ No leagues defined for {current_sport}")

        # 4. Check foreign key integrity
        print("\n=== 4. FOREIGN KEY INTEGRITY ANALYSIS ===")

        # Check teams without sports
        cursor.execute("""
            SELECT COUNT(*) as count FROM teams t
            LEFT JOIN sports s ON t.sport_id = s.id
            WHERE s.id IS NULL
        """)
        teams_without_sports = cursor.fetchone()['count']

        # Check leagues without sports
        cursor.execute("""
            SELECT COUNT(*) as count FROM leagues l
            LEFT JOIN sports s ON l.sport_id = s.id
            WHERE s.id IS NULL
        """)
        leagues_without_sports = cursor.fetchone()['count']

        # Check memberships with invalid teams
        cursor.execute("""
            SELECT COUNT(*) as count FROM team_league_memberships tlm
            LEFT JOIN teams t ON tlm.team_id = t.id
            WHERE t.id IS NULL
        """)
        memberships_invalid_teams = cursor.fetchone()['count']

        # Check memberships with invalid leagues
        cursor.execute("""
            SELECT COUNT(*) as count FROM team_league_memberships tlm
            LEFT JOIN leagues l ON tlm.league_id = l.id
            WHERE l.id IS NULL
        """)
        memberships_invalid_leagues = cursor.fetchone()['count']

        integrity_issues = [
            ("Teams without sports", teams_without_sports),
            ("Leagues without sports", leagues_without_sports),
            ("Memberships with invalid teams", memberships_invalid_teams),
            ("Memberships with invalid leagues", memberships_invalid_leagues)
        ]

        for issue, count in integrity_issues:
            status = "❌" if count > 0 else "✅"
            print(f"{status} {issue:<35} {count:>3}")

        # 5. Check specific onboarding-critical data
        print("\n=== 5. ONBOARDING-CRITICAL DATA ANALYSIS ===")

        # Most popular sports for onboarding
        priority_sports = ["Basketball", "Football", "College Football", "Baseball", "Soccer"]

        for sport_name in priority_sports:
            cursor.execute("""
                SELECT COUNT(DISTINCT t.id) as total_teams,
                       COUNT(DISTINCT CASE WHEN tlm.team_id IS NOT NULL THEN t.id END) as teams_ready
                FROM sports s
                LEFT JOIN teams t ON s.id = t.sport_id AND t.is_active = 1
                LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
                WHERE s.name = ?
            """, (sport_name,))

            result = cursor.fetchone()
            if result and result['total_teams'] > 0:
                ready_pct = (result['teams_ready'] / result['total_teams']) * 100
                status = "✅" if ready_pct == 100 else "❌" if ready_pct < 50 else "⚠"
                print(f"{status} {sport_name:<20} {result['teams_ready']:>3}/{result['total_teams']:<3} ready ({ready_pct:>5.1f}%)")
            else:
                print(f"❌ {sport_name:<20} No teams found")

        # 6. Generate repair summary
        print("\n=== 6. REPAIR SUMMARY ===")
        total_orphaned = len(orphaned_teams)
        total_integrity_issues = sum(count for _, count in integrity_issues)

        if total_orphaned == 0 and total_integrity_issues == 0:
            print("✅ DATABASE IS HEALTHY - No critical issues found")
            return True
        else:
            print(f"❌ CRITICAL ISSUES DETECTED:")
            if total_orphaned > 0:
                print(f"   • {total_orphaned} orphaned teams need league assignments")
            if total_integrity_issues > 0:
                print(f"   • {total_integrity_issues} foreign key integrity violations")

            print("\n🔧 RECOMMENDED ACTIONS:")
            if total_orphaned > 0:
                print("   1. Run team-league assignment repair script")
                print("   2. Create missing league structures for sports")
            if total_integrity_issues > 0:
                print("   3. Clean up broken foreign key references")
            print("   4. Verify onboarding API endpoints can query teams")

            return False

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def get_detailed_orphaned_teams():
    """Get detailed information about orphaned teams for repair"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.id, t.name, t.market, t.abbreviation, t.external_id,
                   s.name as sport, s.id as sport_id
            FROM teams t
            JOIN sports s ON t.sport_id = s.id
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            WHERE tlm.team_id IS NULL AND t.is_active = 1
            ORDER BY s.name, t.market, t.name
        """)

        return cursor.fetchall()

    except Exception as e:
        print(f"Error getting orphaned teams: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    success = analyze_database_integrity()
    sys.exit(0 if success else 1)