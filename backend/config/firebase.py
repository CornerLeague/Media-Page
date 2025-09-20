"""
Firebase configuration and settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class FirebaseConfig(BaseSettings):
    """Firebase configuration settings"""

    # Firebase Project Configuration
    project_id: str = Field(..., env="FIREBASE_PROJECT_ID")

    # Service Account Configuration
    service_account_key_path: Optional[str] = Field(
        None,
        env="FIREBASE_SERVICE_ACCOUNT_KEY_PATH",
        description="Path to Firebase service account key JSON file"
    )

    # Firebase Admin SDK Configuration
    use_emulator: bool = Field(
        default=False,
        env="FIREBASE_USE_EMULATOR",
        description="Whether to use Firebase emulator for development"
    )

    auth_emulator_host: Optional[str] = Field(
        None,
        env="FIREBASE_AUTH_EMULATOR_HOST",
        description="Firebase Auth emulator host (e.g., localhost:9099)"
    )

    # Token Validation Settings
    verify_tokens: bool = Field(
        default=True,
        env="FIREBASE_VERIFY_TOKENS",
        description="Whether to verify Firebase ID tokens"
    )

    check_revoked: bool = Field(
        default=True,
        env="FIREBASE_CHECK_REVOKED",
        description="Whether to check if tokens have been revoked"
    )

    # Security Settings
    require_email_verification: bool = Field(
        default=False,
        env="FIREBASE_REQUIRE_EMAIL_VERIFICATION",
        description="Whether to require email verification for protected routes"
    )

    allowed_audiences: Optional[str] = Field(
        None,
        env="FIREBASE_ALLOWED_AUDIENCES",
        description="Comma-separated list of allowed token audiences"
    )

    # Development Settings
    bypass_auth_in_development: bool = Field(
        default=False,
        env="BYPASS_AUTH_IN_DEVELOPMENT",
        description="Bypass authentication in development (DANGEROUS - only for local dev)"
    )

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

    @property
    def allowed_audiences_list(self) -> Optional[list]:
        """Get allowed audiences as a list"""
        if not self.allowed_audiences:
            return None
        return [aud.strip() for aud in self.allowed_audiences.split(",")]

    def validate_configuration(self) -> None:
        """Validate Firebase configuration"""
        if not self.project_id:
            raise ValueError("FIREBASE_PROJECT_ID environment variable is required")

        if self.use_emulator and not self.auth_emulator_host:
            raise ValueError(
                "FIREBASE_AUTH_EMULATOR_HOST is required when using Firebase emulator"
            )

        if (
            not self.use_emulator
            and not self.service_account_key_path
            and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        ):
            raise ValueError(
                "Either FIREBASE_SERVICE_ACCOUNT_KEY_PATH or GOOGLE_APPLICATION_CREDENTIALS "
                "environment variable is required for production Firebase usage"
            )


# Global configuration instance
firebase_config = FirebaseConfig()


def get_firebase_config() -> FirebaseConfig:
    """Get Firebase configuration instance"""
    return firebase_config


def validate_firebase_environment() -> dict:
    """
    Validate Firebase environment configuration

    Returns:
        dict: Validation results and configuration status
    """
    try:
        config = get_firebase_config()
        config.validate_configuration()

        return {
            "valid": True,
            "project_id": config.project_id,
            "use_emulator": config.use_emulator,
            "has_service_account": bool(config.service_account_key_path),
            "has_google_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            "verify_tokens": config.verify_tokens,
            "require_email_verification": config.require_email_verification
        }

    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "project_id": getattr(firebase_config, "project_id", None)
        }