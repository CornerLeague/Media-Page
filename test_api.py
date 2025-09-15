#!/usr/bin/env python3
"""Test script for the FastAPI application."""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")

    try:
        # Test core imports
        from app.core.config import get_settings
        print("✓ Core config imported")

        from app.core.security import verify_clerk_token
        print("✓ Core security imported")

        # Test models
        from app.models.user import User, CurrentUser
        from app.models.team import Team, TeamResponse
        print("✓ Models imported")

        # Test services
        from app.services.redis_service import RedisService
        from app.services.auth_service import AuthService
        print("✓ Services imported")

        # Test API
        from app.api.main import app
        print("✓ FastAPI app imported")

        return True

    except Exception as e:
        print(f"✗ Import error: {str(e)}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from app.core.config import get_settings
        settings = get_settings()

        print(f"✓ Project name: {settings.PROJECT_NAME}")
        print(f"✓ Version: {settings.VERSION}")
        print(f"✓ API prefix: {settings.API_V1_STR}")
        print(f"✓ Redis URL: {settings.REDIS_URL}")

        return True

    except Exception as e:
        print(f"✗ Configuration error: {str(e)}")
        return False

def test_models():
    """Test Pydantic models."""
    print("\nTesting models...")

    try:
        from app.models.user import CurrentUser, UserPreferences
        from app.models.team import TeamResponse

        # Test CurrentUser model
        user = CurrentUser(
            user_id="test_123",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        print(f"✓ User model: {user.email}")

        # Test Team model
        team_data = {
            "id": "team_1",
            "name": "Test Team",
            "city": "Test City",
            "abbreviation": "TT",
            "sport": "nba",
            "league": "NBA",
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#000000",
            "secondary_color": "#FFFFFF",
            "conference": "Test Conference",
            "division": "Test Division",
            "status": "active",
            "follower_count": 100,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        team = TeamResponse(**team_data)
        print(f"✓ Team model: {team.name}")

        return True

    except Exception as e:
        print(f"✗ Model error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Corner League Media API - Test Suite")
    print("=" * 40)

    tests = [
        test_imports,
        test_configuration,
        test_models
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 40)
    print(f"Tests: {passed}/{total} passed")

    if passed == total:
        print("✓ All tests passed! The API is ready to run.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())