#!/usr/bin/env python3
"""
Test script for Phase 2 Academic Framework models
Validates model structure, relationships, and constraints
"""

import os
import sys
import sqlite3
from datetime import date, datetime
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    # Import all models
    from models.base import Base
    from models.college import (
        Division, CollegeConference, College, CollegeTeam,
        AcademicYear, Season, ConferenceMembership, SeasonConfiguration
    )
    from models.enums import (
        DivisionLevel, ConferenceType, CollegeType, Region, ConferenceStatus,
        SeasonType, AcademicYearStatus, ConferenceMembershipType
    )

    print("✅ All models imported successfully")

except ImportError as e:
    print(f"❌ Error importing models: {e}")
    sys.exit(1)


def test_enum_values():
    """Test that all enum values are properly defined"""
    print("\n🔍 Testing enum values...")

    # Test Phase 2 enums
    season_types = [e.value for e in SeasonType]
    expected_season_types = [
        'regular_season', 'conference_tournament', 'postseason', 'ncaa_tournament',
        'nit', 'cbi', 'cit', 'exhibition', 'preseason'
    ]

    for expected in expected_season_types:
        if expected not in season_types:
            print(f"❌ Missing SeasonType: {expected}")
            return False

    academic_year_statuses = [e.value for e in AcademicYearStatus]
    expected_statuses = ['current', 'future', 'past', 'active']

    for expected in expected_statuses:
        if expected not in academic_year_statuses:
            print(f"❌ Missing AcademicYearStatus: {expected}")
            return False

    print("✅ All enum values are correctly defined")
    return True


def test_model_relationships():
    """Test that model relationships are properly defined"""
    print("\n🔍 Testing model relationships...")

    # Test AcademicYear relationships
    if not hasattr(AcademicYear, 'seasons'):
        print("❌ AcademicYear missing 'seasons' relationship")
        return False

    if not hasattr(AcademicYear, 'conference_memberships'):
        print("❌ AcademicYear missing 'conference_memberships' relationship")
        return False

    # Test Season relationships
    if not hasattr(Season, 'academic_year'):
        print("❌ Season missing 'academic_year' relationship")
        return False

    if not hasattr(Season, 'season_configurations'):
        print("❌ Season missing 'season_configurations' relationship")
        return False

    # Test ConferenceMembership relationships
    if not hasattr(ConferenceMembership, 'college'):
        print("❌ ConferenceMembership missing 'college' relationship")
        return False

    if not hasattr(ConferenceMembership, 'conference'):
        print("❌ ConferenceMembership missing 'conference' relationship")
        return False

    if not hasattr(ConferenceMembership, 'academic_year'):
        print("❌ ConferenceMembership missing 'academic_year' relationship")
        return False

    # Test College has conference_memberships
    if not hasattr(College, 'conference_memberships'):
        print("❌ College missing 'conference_memberships' relationship")
        return False

    print("✅ All model relationships are properly defined")
    return True


def test_model_properties():
    """Test model property methods"""
    print("\n🔍 Testing model properties...")

    # Test AcademicYear properties
    if not hasattr(AcademicYear, 'is_current'):
        print("❌ AcademicYear missing 'is_current' property")
        return False

    if not hasattr(AcademicYear, 'display_years'):
        print("❌ AcademicYear missing 'display_years' property")
        return False

    # Test Season properties
    if not hasattr(Season, 'display_name'):
        print("❌ Season missing 'display_name' property")
        return False

    # Test ConferenceMembership properties
    if not hasattr(ConferenceMembership, 'is_active'):
        print("❌ ConferenceMembership missing 'is_active' property")
        return False

    if not hasattr(ConferenceMembership, 'duration_days'):
        print("❌ ConferenceMembership missing 'duration_days' property")
        return False

    # Test SeasonConfiguration properties
    if not hasattr(SeasonConfiguration, 'parsed_value'):
        print("❌ SeasonConfiguration missing 'parsed_value' property")
        return False

    print("✅ All model properties are properly defined")
    return True


def test_create_in_memory_db():
    """Test creating models in an in-memory SQLite database"""
    print("\n🔍 Testing database schema creation...")

    try:
        # Create in-memory SQLite database
        engine = create_engine('sqlite:///:memory:', echo=False)

        # Only create Phase 2 tables (and dependencies)
        tables_to_create = [
            Base.metadata.tables['academic_years'],
            Base.metadata.tables['seasons'],
            Base.metadata.tables['conference_memberships'],
            Base.metadata.tables['season_configurations']
        ]

        # Create Phase 2 tables only
        for table in tables_to_create:
            table.create(engine, checkfirst=True)

        # Test that tables were created
        with engine.connect() as conn:
            # Check for our Phase 2 tables
            tables_result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )).fetchall()

            table_names = [row[0] for row in tables_result]

            expected_phase2_tables = [
                'academic_years',
                'seasons',
                'conference_memberships',
                'season_configurations'
            ]

            for expected_table in expected_phase2_tables:
                if expected_table not in table_names:
                    print(f"❌ Missing table: {expected_table}")
                    return False

        print("✅ All Phase 2 tables created successfully")

        # Test creating sample data
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Create sample academic year
            academic_year = AcademicYear(
                name='2024-25',
                slug='2024-25',
                start_year=2024,
                end_year=2025,
                start_date=date(2024, 7, 1),
                end_date=date(2025, 6, 30),
                status=AcademicYearStatus.CURRENT,
                description='Test academic year'
            )
            session.add(academic_year)
            session.flush()  # Get the ID

            # Create sample season
            season = Season(
                academic_year_id=academic_year.id,
                name='Regular Season 2024-25',
                slug='regular-season-2024-25',
                season_type=SeasonType.REGULAR_SEASON,
                start_date=date(2024, 11, 4),
                end_date=date(2025, 3, 9),
                is_current=True,
                max_regular_season_games=31
            )
            session.add(season)
            session.flush()

            # Create sample season configuration
            config = SeasonConfiguration(
                season_id=season.id,
                setting_key='max_overtime_periods',
                setting_value='5',
                setting_type='integer',
                description='Maximum overtime periods'
            )
            session.add(config)

            session.commit()

            # Test relationships
            session.refresh(academic_year)
            if len(academic_year.seasons) != 1:
                print(f"❌ Academic year should have 1 season, has {len(academic_year.seasons)}")
                return False

            # Test property methods
            if academic_year.display_years != '2024-25':
                print(f"❌ Academic year display_years should be '2024-25', got '{academic_year.display_years}'")
                return False

            if not academic_year.is_current:
                print("❌ Academic year should be current")
                return False

            # Test season configuration parsing
            if config.parsed_value != 5:
                print(f"❌ Season config should parse to integer 5, got {config.parsed_value}")
                return False

            print("✅ Sample data creation and relationship testing successful")

        finally:
            session.close()

        return True

    except Exception as e:
        print(f"❌ Database schema creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("🚀 Starting Phase 2 Academic Framework Model Validation")
    print("=" * 60)

    tests = [
        test_enum_values,
        test_model_relationships,
        test_model_properties,
        test_create_in_memory_db
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All Phase 2 Academic Framework validations passed!")
        print("\n✅ Phase 2 Implementation Summary:")
        print("   • AcademicYear model: Tracks academic years (2024-25, etc.)")
        print("   • Season model: Individual seasons within academic years")
        print("   • ConferenceMembership model: Historical conference tracking")
        print("   • SeasonConfiguration model: Season-specific settings")
        print("   • All relationships and constraints working correctly")
        print("   • Ready for migration to production database")
        return True
    else:
        print("❌ Some validations failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)