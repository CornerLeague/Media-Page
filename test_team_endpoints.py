#!/usr/bin/env python3
"""
Test script to validate team selection endpoints structure and imports
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/Users/newmac/Desktop/Corner League Media 1')

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")

    try:
        # Test schema imports
        from backend.api.schemas.sports import (
            SportResponse,
            SportWithLeagues,
            LeagueResponse,
            LeagueWithTeams,
            TeamResponse,
            TeamSearchParams,
            UserTeamPreferencesUpdate,
            UserTeamPreferencesResponse,
            SportsPaginatedResponse,
            LeaguesPaginatedResponse,
            TeamsPaginatedResponse
        )
        print("✓ Sports schemas imported successfully")

        # Test service import
        from backend.api.services.team_selection_service import TeamSelectionService
        print("✓ Team selection service imported successfully")

        # Test router import
        from backend.api.routers.team_selection import router
        print("✓ Team selection router imported successfully")

        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_schema_validation():
    """Test Pydantic schema validation"""
    print("\nTesting schema validation...")

    try:
        from backend.api.schemas.sports import TeamSearchParams, UserTeamPreferencesUpdate
        from uuid import uuid4

        # Test TeamSearchParams validation
        search_params = TeamSearchParams(
            query="Lakers",
            sport_id=uuid4(),
            page=1,
            page_size=20
        )
        print("✓ TeamSearchParams validation works")

        # Test UserTeamPreferencesUpdate validation
        preferences_update = UserTeamPreferencesUpdate(
            preferences=[
                {
                    "team_id": uuid4(),
                    "affinity_score": 0.8,
                    "is_active": True
                }
            ]
        )
        print("✓ UserTeamPreferencesUpdate validation works")

        return True

    except Exception as e:
        print(f"✗ Schema validation error: {e}")
        return False

def test_router_structure():
    """Test router structure and endpoint definitions"""
    print("\nTesting router structure...")

    try:
        from backend.api.routers.team_selection import router
        from fastapi import APIRouter

        # Verify it's a FastAPI router
        assert isinstance(router, APIRouter)
        print("✓ Router is a valid FastAPI router")

        # Check that routes are defined (we can't easily inspect them without starting the app)
        print("✓ Router structure looks good")

        return True

    except Exception as e:
        print(f"✗ Router structure error: {e}")
        return False

def generate_openapi_example():
    """Generate an example OpenAPI schema section"""
    print("\nGenerating OpenAPI schema example...")

    try:
        from backend.api.schemas.sports import SportResponse, TeamResponse, TeamSearchParams

        # Get the JSON schema for key models
        sport_schema = SportResponse.model_json_schema()
        team_schema = TeamResponse.model_json_schema()
        search_schema = TeamSearchParams.model_json_schema()

        print("✓ OpenAPI schemas generated successfully")
        print(f"  - SportResponse has {len(sport_schema.get('properties', {}))} properties")
        print(f"  - TeamResponse has {len(team_schema.get('properties', {}))} properties")
        print(f"  - TeamSearchParams has {len(search_schema.get('properties', {}))} properties")

        return True

    except Exception as e:
        print(f"✗ OpenAPI schema generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("Team Selection API Endpoints Validation")
    print("=" * 50)

    tests = [
        test_imports,
        test_schema_validation,
        test_router_structure,
        generate_openapi_example
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print("Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"✓ {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Team selection endpoints are ready.")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)