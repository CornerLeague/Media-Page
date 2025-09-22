#!/usr/bin/env python3
"""
Phase 3: NHL Expansion Validation Script
=========================================

Validates the Phase 3 NHL expansion implementation:
- Professional division structure
- NHL teams and divisions
- Data integrity and quality

Usage:
    python phase3_validation_script.py --db-path sports_platform.db
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any


def validate_phase3_implementation(db_path: str) -> Dict[str, Any]:
    """
    Comprehensive validation of Phase 3 NHL expansion implementation

    Returns:
        Dict containing validation results
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "Phase 3 - NHL Expansion Validation",
        "success": True,
        "errors": [],
        "warnings": [],
        "stats": {},
        "details": {}
    }

    try:
        # 1. Validate professional division tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'professional_divisions'")
        if not cursor.fetchone():
            results["errors"].append("professional_divisions table not found")
            results["success"] = False

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'team_division_memberships'")
        if not cursor.fetchone():
            results["errors"].append("team_division_memberships table not found")
            results["success"] = False

        # 2. Validate NHL divisions
        cursor.execute("""
            SELECT pd.name, pd.conference, COUNT(tdm.team_id) as team_count
            FROM professional_divisions pd
            LEFT JOIN team_division_memberships tdm ON pd.id = tdm.division_id
            JOIN leagues l ON pd.league_id = l.id
            WHERE l.name = 'National Hockey League'
            GROUP BY pd.id, pd.name, pd.conference
            ORDER BY pd.display_order
        """)

        divisions = cursor.fetchall()
        expected_divisions = {
            "Atlantic": {"conference": "Eastern", "expected_teams": 8},
            "Metropolitan": {"conference": "Eastern", "expected_teams": 8},
            "Central": {"conference": "Western", "expected_teams": 8},
            "Pacific": {"conference": "Western", "expected_teams": 8}
        }

        results["details"]["nhl_divisions"] = []
        total_nhl_teams = 0

        for div_name, conference, team_count in divisions:
            division_info = {
                "name": div_name,
                "conference": conference,
                "team_count": team_count,
                "status": "✓"
            }

            if div_name in expected_divisions:
                expected = expected_divisions[div_name]
                if conference != expected["conference"]:
                    results["errors"].append(f"{div_name} in wrong conference: {conference} vs {expected['conference']}")
                    division_info["status"] = "❌"
                    results["success"] = False

                if team_count != expected["expected_teams"]:
                    results["warnings"].append(f"{div_name} has {team_count} teams, expected {expected['expected_teams']}")
                    division_info["status"] = "⚠️"
            else:
                results["warnings"].append(f"Unexpected division: {div_name}")
                division_info["status"] = "?"

            results["details"]["nhl_divisions"].append(division_info)
            total_nhl_teams += team_count

        results["stats"]["total_nhl_teams"] = total_nhl_teams
        results["stats"]["nhl_divisions_created"] = len(divisions)

        # Expected 4 divisions, 32 teams
        if len(divisions) != 4:
            results["errors"].append(f"Expected 4 NHL divisions, found {len(divisions)}")
            results["success"] = False

        if total_nhl_teams != 32:
            results["warnings"].append(f"Expected 32 NHL teams, found {total_nhl_teams}")

        # 3. Validate specific data quality fixes
        cursor.execute("""
            SELECT market, name
            FROM teams
            WHERE (market = 'New England' AND name = 'Patriot')
               OR (market = 'Utah' AND name = 'Mammoth')
        """)

        problem_teams = cursor.fetchall()
        if problem_teams:
            results["errors"].append(f"Data quality issues remain: {problem_teams}")
            results["success"] = False

        # Check correct team names exist
        cursor.execute("""
            SELECT market, name
            FROM teams
            WHERE (market = 'New England' AND name = 'Patriots')
               OR (market = 'Utah' AND name = 'Hockey Club')
        """)

        correct_teams = cursor.fetchall()
        results["details"]["data_quality_fixes"] = [f"{market} {name}" for market, name in correct_teams]

        # 4. Validate team-division memberships
        cursor.execute("""
            SELECT COUNT(*)
            FROM team_division_memberships tdm
            JOIN professional_divisions pd ON tdm.division_id = pd.id
            JOIN leagues l ON pd.league_id = l.id
            WHERE l.name = 'National Hockey League' AND tdm.is_active = 1
        """)

        active_memberships = cursor.fetchone()[0]
        results["stats"]["active_nhl_division_memberships"] = active_memberships

        if active_memberships != total_nhl_teams:
            results["errors"].append(f"Membership count mismatch: {active_memberships} memberships vs {total_nhl_teams} teams")
            results["success"] = False

        # 5. Sample team data for verification
        cursor.execute("""
            SELECT t.market, t.name, pd.name as division, pd.conference
            FROM teams t
            JOIN team_division_memberships tdm ON t.id = tdm.team_id
            JOIN professional_divisions pd ON tdm.division_id = pd.id
            JOIN leagues l ON pd.league_id = l.id
            WHERE l.name = 'National Hockey League'
            ORDER BY pd.conference, pd.name, t.market
            LIMIT 12
        """)

        sample_teams = cursor.fetchall()
        results["details"]["sample_nhl_teams"] = [
            {"market": market, "name": name, "division": division, "conference": conference}
            for market, name, division, conference in sample_teams
        ]

        # 6. Validate indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name = 'professional_divisions'")
        division_indexes = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name = 'team_division_memberships'")
        membership_indexes = [row[0] for row in cursor.fetchall()]

        results["details"]["indexes"] = {
            "professional_divisions": division_indexes,
            "team_division_memberships": membership_indexes
        }

    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Validation error: {str(e)}")

    finally:
        conn.close()

    return results


def print_validation_report(results: Dict[str, Any]):
    """Print a formatted validation report"""
    print("🏒 PHASE 3 NHL EXPANSION VALIDATION REPORT")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Overall Status: {'✅ PASSED' if results['success'] else '❌ FAILED'}")

    if results['errors']:
        print(f"\n❌ ERRORS ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")

    if results['warnings']:
        print(f"\n⚠️  WARNINGS ({len(results['warnings'])}):")
        for warning in results['warnings']:
            print(f"  - {warning}")

    print(f"\n📊 STATISTICS:")
    for key, value in results['stats'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    print(f"\n🏒 NHL DIVISIONS:")
    for division in results['details']['nhl_divisions']:
        print(f"  {division['status']} {division['name']} ({division['conference']} Conference): {division['team_count']} teams")

    print(f"\n🔧 DATA QUALITY FIXES:")
    for fix in results['details']['data_quality_fixes']:
        print(f"  ✓ {fix}")

    print(f"\n🏠 SAMPLE NHL TEAMS:")
    for team in results['details']['sample_nhl_teams'][:8]:
        print(f"  {team['market']} {team['name']} ({team['division']}, {team['conference']})")

    print(f"\n📑 DATABASE INDEXES:")
    print(f"  Professional Divisions: {len(results['details']['indexes']['professional_divisions'])} indexes")
    print(f"  Team Division Memberships: {len(results['details']['indexes']['team_division_memberships'])} indexes")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 3 NHL Expansion Validation")
    parser.add_argument("--db-path", required=True, help="Path to the SQLite database")
    parser.add_argument("--json-output", help="Save results to JSON file")

    args = parser.parse_args()

    # Run validation
    results = validate_phase3_implementation(args.db_path)

    # Print report
    print_validation_report(results)

    # Save JSON output if requested
    if args.json_output:
        with open(args.json_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {args.json_output}")

    # Exit with error code if validation failed
    if not results['success']:
        exit(1)