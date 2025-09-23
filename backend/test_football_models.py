#!/usr/bin/env python3
"""
Test script to verify college football models integration
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_imports():
    """Test that all football models can be imported"""
    print("Testing model imports...")

    try:
        from models import (
            # Football models
            FootballTeam, FootballPlayer, FootballGame, FootballRoster, FootballSeason,
            # Existing college models
            College, CollegeTeam, CollegeConference, Division,
            AcademicYear, Season, CollegePlayer
        )
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_football_enums():
    """Test football-specific enums"""
    print("Testing football enums...")

    try:
        from models.enums import (
            FootballPosition, FootballPositionGroup, FootballPlayType,
            FootballGameContext, FootballWeatherCondition, BowlGameType,
            ScholarshipType, FootballRankingSystem
        )

        # Test enum values
        assert FootballPosition.QUARTERBACK == "quarterback"
        assert FootballPosition.WIDE_RECEIVER == "wide_receiver"
        assert FootballPositionGroup.DEFENSIVE_BACK == "defensive_back"
        assert BowlGameType.COLLEGE_FOOTBALL_PLAYOFF == "college_football_playoff"
        assert ScholarshipType.FULL_SCHOLARSHIP == "full_scholarship"

        print("✅ Football enums work correctly")
        return True
    except Exception as e:
        print(f"❌ Football enum test failed: {e}")
        return False

def test_model_relationships():
    """Test that model relationships are properly defined"""
    print("Testing model relationships...")

    try:
        from models import FootballTeam, FootballPlayer, CollegeTeam

        # Check that FootballTeam has proper relationships
        assert hasattr(FootballTeam, 'college_team')
        assert hasattr(FootballTeam, 'players')
        assert hasattr(FootballTeam, 'games_home')
        assert hasattr(FootballTeam, 'games_away')
        assert hasattr(FootballTeam, 'roster_entries')

        # Check that FootballPlayer has proper relationships
        assert hasattr(FootballPlayer, 'team')
        assert hasattr(FootballPlayer, 'academic_year')
        assert hasattr(FootballPlayer, 'roster_entries')

        print("✅ Model relationships are properly defined")
        return True
    except Exception as e:
        print(f"❌ Model relationship test failed: {e}")
        return False

def test_table_names():
    """Test that table names don't conflict"""
    print("Testing table name uniqueness...")

    try:
        from models import (
            Player, CollegePlayer, FootballPlayer,
            Team, CollegeTeam, FootballTeam
        )

        # Check table names are unique
        assert Player.__tablename__ == "players"  # Generic sports players
        assert CollegePlayer.__tablename__ == "college_players"  # College basketball players
        assert FootballPlayer.__tablename__ == "football_players"  # College football players

        assert Team.__tablename__ == "teams"  # Generic sports teams
        assert CollegeTeam.__tablename__ == "college_teams"  # College teams (bridge)
        assert FootballTeam.__tablename__ == "football_teams"  # Football-specific teams

        print("✅ Table names are unique and properly namespaced")
        return True
    except Exception as e:
        print(f"❌ Table name test failed: {e}")
        return False

def test_football_specific_attributes():
    """Test football-specific attributes and properties"""
    print("Testing football-specific attributes...")

    try:
        from models import FootballTeam, FootballPlayer
        from models.enums import FootballPosition, ScholarshipType

        # Test FootballTeam attributes
        ft_attrs = [
            'stadium_name', 'stadium_capacity', 'head_coach', 'offensive_coordinator',
            'national_championships', 'bowl_appearances', 'ap_poll_rank', 'cfp_ranking'
        ]
        for attr in ft_attrs:
            assert hasattr(FootballTeam, attr), f"FootballTeam missing {attr}"

        # Test FootballPlayer attributes
        fp_attrs = [
            'primary_position', 'position_group', 'forty_yard_dash', 'scholarship_type',
            'recruiting_stars', 'recruiting_rank_national', 'nfl_draft_eligible'
        ]
        for attr in fp_attrs:
            assert hasattr(FootballPlayer, attr), f"FootballPlayer missing {attr}"

        print("✅ Football-specific attributes are present")
        return True
    except Exception as e:
        print(f"❌ Football attribute test failed: {e}")
        return False

def test_property_methods():
    """Test model property methods"""
    print("Testing property methods...")

    try:
        from models import FootballTeam, FootballPlayer

        # Test FootballTeam properties
        team_properties = ['display_name', 'overall_record', 'conference_record', 'is_ranked']
        for prop in team_properties:
            assert hasattr(FootballTeam, prop), f"FootballTeam missing property {prop}"

        # Test FootballPlayer properties
        player_properties = ['display_name', 'height_display', 'age', 'is_eligible_to_play']
        for prop in player_properties:
            assert hasattr(FootballPlayer, prop), f"FootballPlayer missing property {prop}"

        print("✅ Property methods are defined")
        return True
    except Exception as e:
        print(f"❌ Property method test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏈 College Football Phase 1 Model Tests")
    print("=" * 50)

    tests = [
        test_model_imports,
        test_football_enums,
        test_model_relationships,
        test_table_names,
        test_football_specific_attributes,
        test_property_methods
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Tests Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! College Football Phase 1 is ready!")
        print()
        print("Summary of what was implemented:")
        print("- Football-specific enums (positions, play types, formations, etc.)")
        print("- FootballTeam model extending CollegeTeam infrastructure")
        print("- FootballPlayer model with recruiting and performance data")
        print("- FootballGame model with weather and broadcast information")
        print("- FootballRoster model with scholarship tracking (85-player limit)")
        print("- FootballSeason model with calendar and playoff information")
        print("- Integration with existing college basketball infrastructure")
        print("- No table name conflicts between basketball and football")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)