"""
Example demonstrating Firebase JWT authentication middleware integration
"""

from fastapi import FastAPI, Depends, HTTPException, status
from typing import Dict, Any, Optional

# Import the authentication middleware and dependencies
from backend.api.middleware.auth import (
    firebase_auth_required,
    firebase_auth_optional,
    firebase_auth_required_verified
)
from backend.api.services.user_service import (
    get_current_user_context,
    get_current_db_user,
    require_onboarded_user,
    AuthenticatedUserContext
)
from backend.api.schemas.auth import FirebaseUser
from backend.models.users import User
from backend.api.exceptions import register_exception_handlers

# Create FastAPI app
app = FastAPI(title="Auth Integration Example")

# Register exception handlers for proper error responses
register_exception_handlers(app)

# Example 1: Basic protected endpoint
@app.get("/api/profile")
async def get_user_profile(
    firebase_user: FirebaseUser = Depends(firebase_auth_required)
) -> Dict[str, Any]:
    """
    Basic protected endpoint requiring valid Firebase JWT token

    Usage:
    curl -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" http://localhost:8000/api/profile
    """
    return {
        "firebase_uid": firebase_user.uid,
        "email": firebase_user.email,
        "display_name": firebase_user.display_name,
        "email_verified": firebase_user.email_verified
    }

# Example 2: Endpoint requiring verified email
@app.get("/api/sensitive-data")
async def get_sensitive_data(
    firebase_user: FirebaseUser = Depends(firebase_auth_required_verified)
) -> Dict[str, Any]:
    """
    Endpoint requiring valid token AND verified email

    Returns 403 if email is not verified
    """
    return {
        "message": "This is sensitive data only for verified users",
        "user_id": firebase_user.uid
    }

# Example 3: Optional authentication
@app.get("/api/content")
async def get_content(
    firebase_user: Optional[FirebaseUser] = Depends(firebase_auth_optional)
) -> Dict[str, Any]:
    """
    Endpoint with optional authentication - personalizes response if authenticated

    Works without token (public content) or with token (personalized content)
    """
    if firebase_user:
        return {
            "content_type": "personalized",
            "user_id": firebase_user.uid,
            "recommendations": ["Based on your preferences..."]
        }
    else:
        return {
            "content_type": "public",
            "recommendations": ["General recommendations..."]
        }

# Example 4: Database integration with user context
@app.get("/api/dashboard")
async def get_dashboard(
    user_context: AuthenticatedUserContext = Depends(get_current_user_context)
) -> Dict[str, Any]:
    """
    Dashboard endpoint with full user context (Firebase + Database)

    Automatically syncs Firebase user with database if needed
    """
    # Get or create database user
    db_user = await user_context.get_or_create_db_user()

    return {
        "firebase_data": {
            "uid": user_context.firebase_uid,
            "email": user_context.email,
            "verified": user_context.is_verified
        },
        "database_data": {
            "id": str(db_user.id),
            "display_name": db_user.display_name,
            "is_onboarded": db_user.is_onboarded,
            "last_active": db_user.last_active_at.isoformat(),
            "preferences_count": {
                "sports": len(db_user.sport_preferences),
                "teams": len(db_user.team_preferences)
            }
        }
    }

# Example 5: Direct database user dependency
@app.get("/api/preferences")
async def get_preferences(
    db_user: User = Depends(get_current_db_user)
) -> Dict[str, Any]:
    """
    Endpoint that directly provides the database user

    Automatically handles Firebase auth and database lookup
    """
    return {
        "user_id": str(db_user.id),
        "sport_preferences": [
            {
                "sport_name": pref.sport.name if pref.sport else None,
                "rank": pref.rank,
                "is_active": pref.is_active
            }
            for pref in db_user.sport_preferences
        ],
        "team_preferences": [
            {
                "team_name": pref.team.name if pref.team else None,
                "affinity_score": float(pref.affinity_score),
                "is_active": pref.is_active
            }
            for pref in db_user.team_preferences
        ]
    }

# Example 6: Onboarding-required endpoint
@app.get("/api/personalized-feed")
async def get_personalized_feed(
    db_user: User = Depends(require_onboarded_user)
) -> Dict[str, Any]:
    """
    Endpoint requiring completed onboarding

    Returns 403 if user hasn't completed onboarding
    """
    return {
        "message": "Personalized content based on your preferences",
        "user_id": str(db_user.id),
        "feed_items": [
            f"News about your favorite teams: {len(db_user.team_preferences)} teams",
            f"Updates for {len(db_user.sport_preferences)} sports you follow"
        ]
    }

# Example 7: Combined endpoint with multiple user types
@app.post("/api/user-action")
async def perform_user_action(
    action_data: Dict[str, Any],
    user_context: Optional[AuthenticatedUserContext] = Depends(get_current_user_context)
) -> Dict[str, Any]:
    """
    Endpoint that works for both authenticated and unauthenticated users
    """
    if user_context:
        # Authenticated user action
        db_user = await user_context.get_or_create_db_user()

        # Log the action for authenticated user
        return {
            "status": "success",
            "user_type": "authenticated",
            "user_id": str(db_user.id),
            "action": action_data,
            "message": "Action recorded for authenticated user"
        }
    else:
        # Anonymous user action
        return {
            "status": "success",
            "user_type": "anonymous",
            "action": action_data,
            "message": "Action recorded for anonymous user"
        }

# Example 8: Custom authentication logic
@app.get("/api/admin-only")
async def admin_only_endpoint(
    firebase_user: FirebaseUser = Depends(firebase_auth_required)
) -> Dict[str, Any]:
    """
    Example of custom authorization logic using Firebase custom claims
    """
    # Check custom claims for admin role
    if not firebase_user.custom_claims.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return {
        "message": "Welcome, admin!",
        "admin_data": "Sensitive admin information"
    }

# Example 9: Error handling demonstration
@app.get("/api/error-demo/{error_type}")
async def error_demo(
    error_type: str,
    firebase_user: FirebaseUser = Depends(firebase_auth_required)
) -> Dict[str, Any]:
    """
    Demonstrate different error types for testing
    """
    if error_type == "not_found":
        raise HTTPException(status_code=404, detail="Resource not found")
    elif error_type == "forbidden":
        raise HTTPException(status_code=403, detail="Access forbidden")
    elif error_type == "server_error":
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"message": f"No error for type: {error_type}"}

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "auth-example"}

@app.get("/health/auth")
async def auth_health_check():
    """Authentication system health check"""
    from backend.api.middleware.auth import check_firebase_health
    return await check_firebase_health()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)