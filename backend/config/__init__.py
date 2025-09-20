"""
Configuration package for backend settings
"""

from .firebase import (
    FirebaseConfig,
    firebase_config,
    get_firebase_config,
    validate_firebase_environment
)

__all__ = [
    "FirebaseConfig",
    "firebase_config",
    "get_firebase_config",
    "validate_firebase_environment"
]