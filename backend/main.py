"""
FastAPI application with Firebase JWT authentication middleware
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.api.middleware.auth import (
    firebase_auth_required,
    firebase_auth_optional,
    check_firebase_health,
    initialize_firebase
)
from backend.api.services.user_service import (
    get_current_user_context,
    get_current_db_user,
    require_onboarded_user,
    AuthenticatedUserContext
)
from backend.api.services.preference_service import PreferenceService
from backend.api.schemas.preferences import (
    PreferencesUpdate,
    SportsPreferencesUpdate,
    TeamsPreferencesUpdate,
    NotificationPreferencesUpdate
)
from backend.api.routers.team_selection import router as team_selection_router
from backend.api.routers.sports import router as sports_router
from backend.api.routers.onboarding import router as onboarding_router
from backend.database import get_async_session
from backend.api.schemas.auth import FirebaseUser, UserProfile, OnboardingStatus
from backend.api.exceptions import register_exception_handlers
from backend.config.firebase import validate_firebase_environment
from backend.models.users import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting FastAPI application")

    try:
        # Initialize Firebase
        initialize_firebase()
        logger.info("Firebase Admin SDK initialized successfully")

        # Validate configuration
        config_status = validate_firebase_environment()
        if not config_status["valid"]:
            logger.error(f"Firebase configuration invalid: {config_status['error']}")
        else:
            logger.info("Firebase configuration validated successfully")

    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        # You might want to raise here in production to prevent startup with bad config

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application")


# Create FastAPI application
app = FastAPI(
    title="Corner League Media API",
    description="Sports platform API with Firebase authentication",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(",")
)

# Register exception handlers
register_exception_handlers(app)

# Create API v1 sub-application
api_v1 = FastAPI(
    title="Corner League Media API v1",
    description="Sports platform API v1 with Firebase authentication",
    version="1.0.0",
)

# Register exception handlers for API v1 too
register_exception_handlers(api_v1)

# Add user endpoints to API v1
@api_v1.get("/users/me", response_model=UserProfile)
async def get_current_user_api_v1(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> UserProfile:
    """
    Get current authenticated user profile (API v1)

    Requires: Valid Firebase JWT token
    Returns: Complete user profile with preferences
    """
    profile = await user_context.get_user_profile()
    if not profile:
        # Create user if doesn't exist in database
        db_user = await user_context.get_or_create_db_user()
        return UserProfile.from_orm(db_user)
    return profile


@api_v1.put("/users/me", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def create_or_update_user_api_v1(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> UserProfile:
    """
    Create or update user profile (API v1)

    Requires: Valid Firebase JWT token
    Returns: Created or updated user profile
    """
    db_user = await user_context.get_or_create_db_user()
    return UserProfile.from_orm(db_user)


@api_v1.get("/auth/onboarding-status", response_model=OnboardingStatus)
async def get_onboarding_status_api_v1(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> OnboardingStatus:
    """
    Get user onboarding status (API v1)

    Requires: Valid Firebase JWT token
    Returns: Onboarding completion status and current step
    """
    db_user = await user_context.get_or_create_db_user()

    return OnboardingStatus(
        hasCompletedOnboarding=db_user.is_onboarded,
        currentStep=db_user.current_onboarding_step
    )


@api_v1.get("/me/home")
async def get_home_data_api_v1(
    db_user: User = Depends(get_current_db_user)
) -> Dict[str, Any]:
    """
    Get user home dashboard data (API v1)

    Requires: Valid Firebase JWT token
    Returns: Home dashboard data with user teams and preferences
    """
    # Find most liked team (highest affinity score)
    most_liked_team = None
    most_liked_team_id = None

    if db_user.team_preferences:
        max_affinity = max(pref.affinity_score for pref in db_user.team_preferences)
        most_liked_team = next(
            pref for pref in db_user.team_preferences
            if pref.affinity_score == max_affinity
        )
        most_liked_team_id = str(most_liked_team.team_id) if most_liked_team else None

    return {
        "most_liked_team_id": most_liked_team_id,
        "user_teams": [
            {
                "team_id": str(pref.team_id),
                "name": pref.team.name if pref.team else None,
                "affinity_score": float(pref.affinity_score)
            }
            for pref in db_user.team_preferences
            if pref.is_active
        ]
    }

# Add preferences endpoint to API v1
@api_v1.get("/me/preferences")
async def get_user_preferences_api_v1(
    db_user: User = Depends(get_current_db_user)
) -> Dict[str, Any]:
    """
    Get user preferences (API v1)

    Requires: Valid Firebase JWT token
    Returns: User's sports, teams, and notification preferences
    """
    return {
        "sport_preferences": [
            {
                "id": str(pref.id),
                "sport_id": str(pref.sport_id),
                "sport_name": pref.sport.name if pref.sport else None,
                "rank": pref.rank,
                "is_active": pref.is_active
            }
            for pref in db_user.sport_preferences
        ],
        "team_preferences": [
            {
                "id": str(pref.id),
                "team_id": str(pref.team_id),
                "team_name": pref.team.name if pref.team else None,
                "affinity_score": float(pref.affinity_score),
                "is_active": pref.is_active
            }
            for pref in db_user.team_preferences
        ],
        "notification_settings": {
            "push_enabled": db_user.notification_settings.push_enabled if db_user.notification_settings else False,
            "email_enabled": db_user.notification_settings.email_enabled if db_user.notification_settings else False,
            "game_reminders": db_user.notification_settings.game_reminders if db_user.notification_settings else False,
            "news_alerts": db_user.notification_settings.news_alerts if db_user.notification_settings else False,
            "score_updates": db_user.notification_settings.score_updates if db_user.notification_settings else False
        } if db_user.notification_settings else None
    }


# Preference service dependency
async def get_preference_service(db: AsyncSession = Depends(get_async_session)) -> PreferenceService:
    """Dependency to get PreferenceService instance"""
    return PreferenceService(db)


@api_v1.put("/me/preferences")
async def update_user_preferences_api_v1(
    preferences_update: PreferencesUpdate,
    db_user: User = Depends(get_current_db_user),
    preference_service: PreferenceService = Depends(get_preference_service)
) -> Dict[str, Any]:
    """
    Update user preferences (bulk update) (API v1)

    Requires: Valid Firebase JWT token
    Returns: Updated preference data
    """
    result = await preference_service.update_user_preferences(db_user, preferences_update)

    # Return current state of all preferences after update
    current_preferences = {
        "sport_preferences": [
            {
                "id": str(pref.id),
                "sport_id": str(pref.sport_id),
                "sport_name": pref.sport.name if pref.sport else None,
                "rank": pref.rank,
                "is_active": pref.is_active
            }
            for pref in db_user.sport_preferences
        ],
        "team_preferences": [
            {
                "id": str(pref.id),
                "team_id": str(pref.team_id),
                "team_name": pref.team.name if pref.team else None,
                "affinity_score": float(pref.affinity_score),
                "is_active": pref.is_active
            }
            for pref in db_user.team_preferences
        ],
        "notification_settings": {
            "push_enabled": db_user.notification_settings.push_enabled if db_user.notification_settings else False,
            "email_enabled": db_user.notification_settings.email_enabled if db_user.notification_settings else False,
            "game_reminders": db_user.notification_settings.game_reminders if db_user.notification_settings else False,
            "news_alerts": db_user.notification_settings.news_alerts if db_user.notification_settings else False,
            "score_updates": db_user.notification_settings.score_updates if db_user.notification_settings else False
        } if db_user.notification_settings else None,
        "content_frequency": db_user.content_frequency
    }

    return current_preferences


@api_v1.put("/me/preferences/sports")
async def update_sports_preferences_api_v1(
    sports_update: SportsPreferencesUpdate,
    db_user: User = Depends(get_current_db_user),
    preference_service: PreferenceService = Depends(get_preference_service)
) -> Dict[str, Any]:
    """
    Update user sports preferences (API v1)

    Requires: Valid Firebase JWT token
    Returns: Updated sports preferences
    """
    sport_prefs = await preference_service.update_sport_preferences(db_user, sports_update.sports)

    return {
        "sport_preferences": [
            {
                "id": str(pref.id),
                "sport_id": str(pref.sport_id),
                "sport_name": pref.sport.name if pref.sport else None,
                "rank": pref.rank,
                "is_active": pref.is_active
            }
            for pref in sport_prefs
        ]
    }


@api_v1.put("/me/preferences/teams")
async def update_teams_preferences_api_v1(
    teams_update: TeamsPreferencesUpdate,
    db_user: User = Depends(get_current_db_user),
    preference_service: PreferenceService = Depends(get_preference_service)
) -> Dict[str, Any]:
    """
    Update user team preferences (API v1)

    Requires: Valid Firebase JWT token
    Returns: Updated team preferences
    """
    team_prefs = await preference_service.update_team_preferences(db_user, teams_update.teams)

    return {
        "team_preferences": [
            {
                "id": str(pref.id),
                "team_id": str(pref.team_id),
                "team_name": pref.team.name if pref.team else None,
                "affinity_score": float(pref.affinity_score),
                "is_active": pref.is_active
            }
            for pref in team_prefs
        ]
    }


@api_v1.put("/me/preferences/notifications")
async def update_notification_preferences_api_v1(
    notifications_update: NotificationPreferencesUpdate,
    db_user: User = Depends(get_current_db_user),
    preference_service: PreferenceService = Depends(get_preference_service)
) -> Dict[str, Any]:
    """
    Update user notification preferences (API v1)

    Requires: Valid Firebase JWT token
    Returns: Updated notification preferences
    """
    notification_settings = await preference_service.update_notification_preferences(
        db_user, notifications_update
    )

    return {
        "notification_settings": {
            "push_enabled": notification_settings.push_enabled,
            "email_enabled": notification_settings.email_enabled,
            "game_reminders": notification_settings.game_reminders,
            "news_alerts": notification_settings.news_alerts,
            "score_updates": notification_settings.score_updates
        }
    }

# Mount API v1 sub-application
app.mount("/api/v1", api_v1)

# Include routers in main app
app.include_router(team_selection_router)
app.include_router(sports_router)
app.include_router(onboarding_router)

# Also include routers in API v1
api_v1.include_router(team_selection_router)
api_v1.include_router(sports_router)
api_v1.include_router(onboarding_router)


# Health check endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "corner-league-api",
        "version": "1.0.0"
    }


@app.get("/health/firebase")
async def firebase_health_check() -> Dict[str, Any]:
    """Firebase connectivity health check"""
    return await check_firebase_health()


@app.get("/health/config")
async def config_health_check() -> Dict[str, Any]:
    """Configuration validation health check"""
    return validate_firebase_environment()


# Authentication endpoints
@app.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> UserProfile:
    """
    Get current authenticated user profile

    Requires: Valid Firebase JWT token
    Returns: Complete user profile with preferences
    """
    profile = await user_context.get_user_profile()
    if not profile:
        # Create user if doesn't exist in database
        db_user = await user_context.get_or_create_db_user()
        return UserProfile.from_orm(db_user)
    return profile


@app.get("/auth/firebase", response_model=FirebaseUser)
async def get_firebase_user(
    firebase_user: FirebaseUser = Depends(firebase_auth_required)
) -> FirebaseUser:
    """
    Get Firebase user information from JWT token

    Requires: Valid Firebase JWT token
    Returns: Firebase user data extracted from token
    """
    return firebase_user


@app.post("/auth/sync-user", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def sync_user_with_database(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> UserProfile:
    """
    Sync Firebase user with database (create or update)

    Requires: Valid Firebase JWT token
    Returns: Updated user profile
    """
    db_user = await user_context.get_or_create_db_user()
    return UserProfile.from_orm(db_user)


@app.get("/auth/onboarding-status", response_model=OnboardingStatus)
async def get_onboarding_status(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> OnboardingStatus:
    """
    Get user onboarding status

    Requires: Valid Firebase JWT token
    Returns: Onboarding completion status and current step
    """
    db_user = await user_context.get_or_create_db_user()

    return OnboardingStatus(
        hasCompletedOnboarding=db_user.is_onboarded,
        currentStep=db_user.current_onboarding_step
    )


# User profile endpoints
@app.get("/me", response_model=UserProfile)
async def get_current_user(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> UserProfile:
    """
    Get current authenticated user profile

    Requires: Valid Firebase JWT token
    Returns: Complete user profile with preferences
    """
    profile = await user_context.get_user_profile()
    if not profile:
        # Create user if doesn't exist in database
        db_user = await user_context.get_or_create_db_user()
        return UserProfile.from_orm(db_user)
    return profile


@app.get("/users/me", response_model=UserProfile)
async def get_current_user_users_path(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> UserProfile:
    """
    Get current authenticated user profile (frontend API client compatibility)

    Requires: Valid Firebase JWT token
    Returns: Complete user profile with preferences
    """
    profile = await user_context.get_user_profile()
    if not profile:
        # Create user if doesn't exist in database
        db_user = await user_context.get_or_create_db_user()
        return UserProfile.from_orm(db_user)
    return profile


# Protected endpoints (examples)
@app.get("/me/dashboard")
async def get_user_dashboard(
    db_user: User = Depends(require_onboarded_user)
) -> Dict[str, Any]:
    """
    Get user dashboard data

    Requires: Valid Firebase JWT token + completed onboarding
    Returns: Personalized dashboard data
    """
    return {
        "user_id": str(db_user.id),
        "display_name": db_user.display_name,
        "is_onboarded": db_user.is_onboarded,
        "sport_preferences_count": len(db_user.sport_preferences),
        "team_preferences_count": len(db_user.team_preferences),
        "last_active": db_user.last_active_at.isoformat()
    }


@app.get("/me/preferences")
async def get_user_preferences(
    db_user: User = Depends(get_current_db_user)
) -> Dict[str, Any]:
    """
    Get user preferences

    Requires: Valid Firebase JWT token
    Returns: User's sports, teams, and notification preferences
    """
    return {
        "sport_preferences": [
            {
                "id": str(pref.id),
                "sport_id": str(pref.sport_id),
                "sport_name": pref.sport.name if pref.sport else None,
                "rank": pref.rank,
                "is_active": pref.is_active
            }
            for pref in db_user.sport_preferences
        ],
        "team_preferences": [
            {
                "id": str(pref.id),
                "team_id": str(pref.team_id),
                "team_name": pref.team.name if pref.team else None,
                "affinity_score": float(pref.affinity_score),
                "is_active": pref.is_active
            }
            for pref in db_user.team_preferences
        ],
        "notification_settings": {
            "push_enabled": db_user.notification_settings.push_enabled if db_user.notification_settings else False,
            "email_enabled": db_user.notification_settings.email_enabled if db_user.notification_settings else False,
            "game_reminders": db_user.notification_settings.game_reminders if db_user.notification_settings else False,
            "news_alerts": db_user.notification_settings.news_alerts if db_user.notification_settings else False,
            "score_updates": db_user.notification_settings.score_updates if db_user.notification_settings else False
        } if db_user.notification_settings else None
    }


# Optional authentication endpoints (examples)
@app.get("/public/sports")
async def get_public_sports(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context),
    # This would normally depend on your sports service
) -> Dict[str, Any]:
    """
    Get public sports data with optional personalization

    Optional: Firebase JWT token for personalization
    Returns: Sports data, personalized if user is authenticated
    """
    # Example of optional authentication - customize response based on user
    if user_context and user_context.db_user:
        return {
            "sports": "personalized_sports_data",
            "user_preferences": True,
            "user_id": str(user_context.db_user.id)
        }
    else:
        return {
            "sports": "public_sports_data",
            "user_preferences": False
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV") == "development",
        log_level="info"
    )