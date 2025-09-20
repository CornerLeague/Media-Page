"""
Middleware package for FastAPI authentication and request processing
"""

from .auth import (
    FirebaseJWTMiddleware,
    FirebaseAuthRequired,
    FirebaseAuthOptional,
    AuthError,
    firebase_auth_required,
    firebase_auth_required_verified,
    firebase_auth_optional,
    get_current_user_id,
    get_current_user_email,
    check_firebase_health,
    initialize_firebase
)

__all__ = [
    "FirebaseJWTMiddleware",
    "FirebaseAuthRequired",
    "FirebaseAuthOptional",
    "AuthError",
    "firebase_auth_required",
    "firebase_auth_required_verified",
    "firebase_auth_optional",
    "get_current_user_id",
    "get_current_user_email",
    "check_firebase_health",
    "initialize_firebase"
]