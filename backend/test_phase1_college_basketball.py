#!/usr/bin/env python3
"""
Test script for Phase 1 College Basketball Migration
Tests the foundation schema and seed data
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_phase1_migration():
    """Test Phase 1 college basketball migration on SQLite."""

    # Use the existing SQLite database
    db_path = backend_path / "sports_platform.db"

    if not db_path.exists():
        print("❌ Database file not found. Please ensure the database exists.")
        return False

    print(f"🔍 Testing Phase 1 college basketball migration on {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Test 1: Check if tables exist
        print("\n📊 Testing table creation...")

        tables_to_check = [
            'divisions',
            'college_conferences',
            'colleges',
            'college_teams'
        ]

        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            if result:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' not found")
                return False

        # Test 2: Check Division I exists
        print("\n📊 Testing division data...")
        cursor.execute("SELECT COUNT(*) FROM divisions WHERE slug = 'division-i'")
        division_count = cursor.fetchone()[0]
        if division_count > 0:
            print(f"✅ Division I found ({division_count} record)")
        else:
            print("❌ Division I not found")
            return False

        # Test 3: Check conferences count
        print("\n📊 Testing conference data...")
        cursor.execute("SELECT COUNT(*) FROM college_conferences")
        conference_count = cursor.fetchone()[0]
        print(f"✅ Found {conference_count} conferences")

        # List conferences
        cursor.execute("SELECT name, abbreviation FROM college_conferences ORDER BY name")
        conferences = cursor.fetchall()
        for conf_name, conf_abbr in conferences:
            print(f"   - {conf_name} ({conf_abbr})")

        # Test 4: Check colleges count
        print("\n📊 Testing college data...")
        cursor.execute("SELECT COUNT(*) FROM colleges")
        college_count = cursor.fetchone()[0]
        print(f"✅ Found {college_count} colleges")

        # Test 5: Check college teams count
        print("\n📊 Testing college teams data...")
        cursor.execute("SELECT COUNT(*) FROM college_teams")
        team_count = cursor.fetchone()[0]
        print(f"✅ Found {team_count} college teams")

        # Test 6: Test specific conference team counts
        print("\n📊 Testing team distribution by conference...")
        cursor.execute("""
            SELECT cc.abbreviation, COUNT(ct.id) as team_count
            FROM college_conferences cc
            LEFT JOIN colleges c ON c.conference_id = cc.id
            LEFT JOIN college_teams ct ON ct.college_id = c.id
            GROUP BY cc.id, cc.abbreviation
            ORDER BY cc.abbreviation
        """)

        conference_teams = cursor.fetchall()
        total_teams = 0
        for conf_abbr, count in conference_teams:
            print(f"   {conf_abbr}: {count} teams")
            total_teams += count

        print(f"\n📊 Total teams across all conferences: {total_teams}")

        # Test 7: Check data integrity
        print("\n📊 Testing data integrity...")

        # Check for orphaned records
        cursor.execute("""
            SELECT COUNT(*) FROM colleges
            WHERE conference_id NOT IN (SELECT id FROM college_conferences)
        """)
        orphaned_colleges = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM college_teams
            WHERE college_id NOT IN (SELECT id FROM colleges)
        """)
        orphaned_teams = cursor.fetchone()[0]

        if orphaned_colleges == 0 and orphaned_teams == 0:
            print("✅ No orphaned records found - data integrity maintained")
        else:
            print(f"❌ Found {orphaned_colleges} orphaned colleges and {orphaned_teams} orphaned teams")
            return False

        # Test 8: Test some sample queries
        print("\n📊 Testing sample queries...")

        # Top conferences by team count
        cursor.execute("""
            SELECT cc.name, COUNT(ct.id) as team_count
            FROM college_conferences cc
            LEFT JOIN colleges c ON c.conference_id = cc.id
            LEFT JOIN college_teams ct ON ct.college_id = c.id
            GROUP BY cc.id, cc.name
            ORDER BY team_count DESC
            LIMIT 5
        """)

        top_conferences = cursor.fetchall()
        print("Top 5 conferences by team count:")
        for conf_name, count in top_conferences:
            print(f"   {conf_name}: {count} teams")

        # Sample teams from each major conference
        cursor.execute("""
            SELECT cc.abbreviation, c.name as college_name, ct.name as team_name
            FROM college_teams ct
            JOIN colleges c ON ct.college_id = c.id
            JOIN college_conferences cc ON c.conference_id = cc.id
            WHERE cc.abbreviation IN ('ACC', 'SEC', 'Big Ten', 'Big 12', 'Big East')
            ORDER BY cc.abbreviation, c.name
            LIMIT 20
        """)

        sample_teams = cursor.fetchall()
        print("\nSample teams from major conferences:")
        current_conf = None
        for conf_abbr, college_name, team_name in sample_teams:
            if conf_abbr != current_conf:
                print(f"\n  {conf_abbr}:")
                current_conf = conf_abbr
            print(f"    {college_name} {team_name}")

        print("\n🎉 All Phase 1 tests passed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()


def test_rollback_capability():
    """Test the rollback capability by checking the downgrade function."""
    print("\n🔄 Testing rollback capability...")

    # Read the migration file to verify downgrade function exists
    migration_file = backend_path / "alembic" / "versions" / "20250921_1635_phase1_college_basketball_seed_data.py"

    if not migration_file.exists():
        print("❌ Migration file not found")
        return False

    with open(migration_file, 'r') as f:
        content = f.read()

    if 'def downgrade()' in content and 'DELETE FROM' in content:
        print("✅ Rollback function exists and contains cleanup operations")
        return True
    else:
        print("❌ Rollback function missing or incomplete")
        return False


def main():
    """Main test runner."""
    print("🚀 Starting Phase 1 College Basketball Migration Tests")
    print("=" * 60)

    # Test migration
    migration_success = test_phase1_migration()

    # Test rollback capability
    rollback_success = test_rollback_capability()

    print("\n" + "=" * 60)
    if migration_success and rollback_success:
        print("🎉 ALL TESTS PASSED - Phase 1 implementation is ready!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please review the implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())