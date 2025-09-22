"""
Pytest configuration and fixtures for Corner League Media backend testing.

This module provides shared fixtures for database setup, Firebase authentication mocking,
and other testing utilities used across all test modules.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.base import Base
from backend.models.users import User
from backend.models.sports import Sport, Team
from backend.database import get_async_session


# Test Database Setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with rollback."""
    TestSessionLocal = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with TestSessionLocal() as session:
        # Start a transaction
        transaction = await session.begin()

        yield session

        # Rollback the transaction to clean up
        await transaction.rollback()


@pytest.fixture
async def test_client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database session."""

    async def override_get_async_session():
        yield test_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sync_test_client() -> TestClient:
    """Create a synchronous test client for simple tests."""
    return TestClient(app)


# Mock Firebase Authentication Fixtures

@pytest.fixture
def mock_firebase_user():
    """Mock Firebase user data."""
    return {
        "uid": "test-firebase-uid-123",
        "email": "test@example.com",
        "email_verified": True,
        "display_name": "Test User",
        "phone_number": None,
        "photo_url": None,
        "disabled": False,
        "custom_claims": {},
        "provider_data": [],
        "metadata": {
            "creation_timestamp": 1609459200,  # 2021-01-01
            "last_sign_in_timestamp": 1640995200,  # 2022-01-01
        }
    }


@pytest.fixture
def mock_firebase_token():
    """Mock Firebase ID token."""
    return {
        "iss": "https://securetoken.google.com/test-project",
        "aud": "test-project",
        "auth_time": 1640995200,
        "user_id": "test-firebase-uid-123",
        "sub": "test-firebase-uid-123",
        "iat": 1640995200,
        "exp": 1640998800,
        "email": "test@example.com",
        "email_verified": True,
        "firebase": {
            "identities": {
                "email": ["test@example.com"]
            },
            "sign_in_provider": "password"
        }
    }


@pytest.fixture
def mock_auth_header(mock_firebase_token):
    """Mock authorization header for authenticated requests."""
    return {"Authorization": "Bearer mock-firebase-token"}


@pytest.fixture
def mock_firebase_auth(mock_firebase_user, mock_firebase_token):
    """Mock Firebase Admin SDK authentication."""
    with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
         patch('firebase_admin.auth.get_user') as mock_get_user:

        mock_verify.return_value = mock_firebase_token
        mock_get_user.return_value = Mock(**mock_firebase_user)

        yield {
            'verify_token': mock_verify,
            'get_user': mock_get_user
        }


# Test Data Fixtures

@pytest.fixture
async def test_user(test_session: AsyncSession, mock_firebase_user) -> User:
    """Create a test user in the database."""
    user = User(
        id=UUID('12345678-1234-5678-1234-567812345678'),
        firebase_uid=mock_firebase_user["uid"],
        email=mock_firebase_user["email"],
        display_name=mock_firebase_user["display_name"],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_active_at=datetime.utcnow(),
        current_onboarding_step=1,
        onboarding_completed_at=None
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest.fixture
async def completed_onboarding_user(test_session: AsyncSession, mock_firebase_user) -> User:
    """Create a test user who has completed onboarding."""
    user = User(
        id=UUID('87654321-4321-8765-4321-876543218765'),
        firebase_uid=f"{mock_firebase_user['uid']}-completed",
        email="completed@example.com",
        display_name="Completed User",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_active_at=datetime.utcnow(),
        current_onboarding_step=None,
        onboarding_completed_at=datetime.utcnow()
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest.fixture
async def test_sports(test_session: AsyncSession) -> list[Sport]:
    """Create test sports data."""
    sports_data = [
        {
            "id": UUID('11111111-1111-1111-1111-111111111111'),
            "name": "Football",
            "slug": "football",
            "icon": "🏈",
            "icon_url": "https://example.com/football.png",
            "description": "American Football",
            "popularity_rank": 1,
            "is_active": True
        },
        {
            "id": UUID('22222222-2222-2222-2222-222222222222'),
            "name": "Basketball",
            "slug": "basketball",
            "icon": "🏀",
            "icon_url": "https://example.com/basketball.png",
            "description": "Basketball",
            "popularity_rank": 2,
            "is_active": True
        },
        {
            "id": UUID('33333333-3333-3333-3333-333333333333'),
            "name": "Baseball",
            "slug": "baseball",
            "icon": "⚾",
            "icon_url": "https://example.com/baseball.png",
            "description": "Baseball",
            "popularity_rank": 3,
            "is_active": True
        },
        {
            "id": UUID('44444444-4444-4444-4444-444444444444'),
            "name": "Hockey",
            "slug": "hockey",
            "icon": "🏒",
            "icon_url": "https://example.com/hockey.png",
            "description": "Ice Hockey",
            "popularity_rank": 4,
            "is_active": False  # Inactive sport for testing
        }
    ]

    sports = []
    for sport_data in sports_data:
        sport = Sport(**sport_data)
        test_session.add(sport)
        sports.append(sport)

    await test_session.commit()

    for sport in sports:
        await test_session.refresh(sport)

    return sports


@pytest.fixture
async def test_teams(test_session: AsyncSession, test_sports: list[Sport]) -> list[Team]:
    """Create test teams data."""
    teams_data = [
        # Football teams
        {
            "id": UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
            "name": "Patriots",
            "market": "New England",
            "slug": "patriots",
            "sport_id": test_sports[0].id,  # Football
            "logo_url": "https://example.com/patriots.png",
            "abbreviation": "NE",
            "primary_color": "#002244",
            "secondary_color": "#C60C30",
            "is_active": True
        },
        {
            "id": UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
            "name": "Chiefs",
            "market": "Kansas City",
            "slug": "chiefs",
            "sport_id": test_sports[0].id,  # Football
            "logo_url": "https://example.com/chiefs.png",
            "abbreviation": "KC",
            "primary_color": "#E31837",
            "secondary_color": "#FFB81C",
            "is_active": True
        },
        # Basketball teams
        {
            "id": UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
            "name": "Lakers",
            "market": "Los Angeles",
            "slug": "lakers",
            "sport_id": test_sports[1].id,  # Basketball
            "logo_url": "https://example.com/lakers.png",
            "abbreviation": "LAL",
            "primary_color": "#552583",
            "secondary_color": "#FDB927",
            "is_active": True
        },
        {
            "id": UUID('dddddddd-dddd-dddd-dddd-dddddddddddd'),
            "name": "Celtics",
            "market": "Boston",
            "slug": "celtics",
            "sport_id": test_sports[1].id,  # Basketball
            "logo_url": "https://example.com/celtics.png",
            "abbreviation": "BOS",
            "primary_color": "#007A33",
            "secondary_color": "#BA9653",
            "is_active": True
        }
    ]

    teams = []
    for team_data in teams_data:
        team = Team(**team_data)
        test_session.add(team)
        teams.append(team)

    await test_session.commit()

    for team in teams:
        await test_session.refresh(team)

    return teams


# Authentication Helper Fixtures

@pytest.fixture
def authenticated_headers(mock_firebase_auth, mock_auth_header):
    """Headers for authenticated requests."""
    return mock_auth_header


@pytest.fixture
def unauthenticated_headers():
    """Headers for unauthenticated requests."""
    return {}


# Performance Testing Fixtures

@pytest.fixture
def performance_threshold():
    """Performance thresholds for API response times."""
    return {
        "fast": 0.1,      # 100ms
        "acceptable": 0.5, # 500ms
        "slow": 2.0       # 2 seconds
    }


# Mock External Services

@pytest.fixture
def mock_redis():
    """Mock Redis connection for caching tests."""
    with patch('redis.Redis') as mock:
        yield mock


@pytest.fixture
def mock_firebase_messaging():
    """Mock Firebase Cloud Messaging for notification tests."""
    with patch('firebase_admin.messaging.send') as mock:
        yield mock


# Utility Functions

def assert_uuid(value: str) -> UUID:
    """Assert that a string value is a valid UUID and return it."""
    try:
        return UUID(value)
    except (ValueError, TypeError):
        pytest.fail(f"Expected valid UUID, got: {value}")


def assert_datetime(value: str) -> datetime:
    """Assert that a string value is a valid ISO datetime and return it."""
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        pytest.fail(f"Expected valid ISO datetime, got: {value}")


# Custom Assertions

def assert_response_structure(response_data: dict, required_fields: list[str]):
    """Assert that a response contains all required fields."""
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"


def assert_error_response(response_data: dict, expected_code: str = None):
    """Assert that a response is a proper error response."""
    assert "detail" in response_data, "Error response must contain 'detail' field"
    if expected_code:
        assert response_data.get("detail") == expected_code or expected_code in str(response_data.get("detail"))