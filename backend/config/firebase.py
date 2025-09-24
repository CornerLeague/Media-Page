"""
Firebase configuration and settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class FirebaseConfig(BaseSettings):
    """Firebase configuration settings"""

    # Firebase Project Configuration
    project_id: Optional[str] = Field(
        default=None,
        env="FIREBASE_PROJECT_ID",
        description="Firebase project ID - required for production use"
    )

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

    allow_mock_tokens: bool = Field(
        default=False,
        env="ALLOW_FIREBASE_MOCK_TOKENS",
        description="Allow mock Firebase tokens for local development scenarios"
    )

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # Allow extra fields to prevent validation errors
        env_ignore_empty=True,  # Ignore empty env vars
        validate_assignment=False  # Don't validate on assignment
    )

    @property
    def allowed_audiences_list(self) -> Optional[list]:
        """Get allowed audiences as a list"""
        if not self.allowed_audiences:
            return None
        return [aud.strip() for aud in self.allowed_audiences.split(",")]

    def validate_configuration(self) -> None:
        """
        Validate Firebase configuration with detailed error messages

        Raises:
            ValueError: If configuration is invalid with specific guidance
        """
        errors = []

        # Check for required project ID
        if not self.project_id:
            errors.append(
                "FIREBASE_PROJECT_ID environment variable is required. "
                "Set it in your .env file or environment variables."
            )

        # Check emulator configuration
        if self.use_emulator and not self.auth_emulator_host:
            errors.append(
                "FIREBASE_AUTH_EMULATOR_HOST is required when FIREBASE_USE_EMULATOR=true. "
                "Example: FIREBASE_AUTH_EMULATOR_HOST=localhost:9099"
            )

        # Check production credentials
        if (
            not self.use_emulator
            and not self.bypass_auth_in_development
            and not self.service_account_key_path
            and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        ):
            errors.append(
                "Firebase credentials are required for production use. "
                "Set either FIREBASE_SERVICE_ACCOUNT_KEY_PATH (path to service account JSON) "
                "or GOOGLE_APPLICATION_CREDENTIALS environment variable. "
                "For local development, you can set FIREBASE_USE_EMULATOR=true or "
                "BYPASS_AUTH_IN_DEVELOPMENT=true (not recommended)."
            )

        if errors:
            error_message = "Firebase configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_message)

    def is_properly_configured(self) -> bool:
        """
        Check if Firebase configuration is valid without raising exceptions

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            self.validate_configuration()
            return True
        except ValueError:
            return False


# Global configuration instance - handle missing required fields gracefully
firebase_config: Optional[FirebaseConfig] = None

def _initialize_firebase_config(load_dotenv_file: bool = True) -> Optional[FirebaseConfig]:
    """
    Initialize Firebase configuration with proper error handling

    Args:
        load_dotenv_file: Whether to load .env file (set to False in tests)

    Returns:
        FirebaseConfig instance or None if initialization fails
    """
    try:
        # Optionally load .env file
        if load_dotenv_file:
            from dotenv import load_dotenv
            import os

            # Try to load .env from current directory and parent directory
            env_paths = [".env", "../.env"]
            for env_path in env_paths:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    break

        # Create config with explicit environment variable mapping
        # This works around Pydantic v2 env_file issues
        config_data = {
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "service_account_key_path": os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH"),
            "use_emulator": _str_to_bool(os.getenv("FIREBASE_USE_EMULATOR", "false")),
            "auth_emulator_host": os.getenv("FIREBASE_AUTH_EMULATOR_HOST"),
            "verify_tokens": _str_to_bool(os.getenv("FIREBASE_VERIFY_TOKENS", "true")),
            "check_revoked": _str_to_bool(os.getenv("FIREBASE_CHECK_REVOKED", "true")),
            "require_email_verification": _str_to_bool(os.getenv("FIREBASE_REQUIRE_EMAIL_VERIFICATION", "false")),
            "allowed_audiences": os.getenv("FIREBASE_ALLOWED_AUDIENCES"),
            "bypass_auth_in_development": _str_to_bool(os.getenv("BYPASS_AUTH_IN_DEVELOPMENT", "false")),
            "allow_mock_tokens": _str_to_bool(os.getenv("ALLOW_FIREBASE_MOCK_TOKENS", "false")),
        }

        # Filter out None values to use defaults
        config_data = {k: v for k, v in config_data.items() if v is not None}

        config = FirebaseConfig(**config_data)
        return config
    except Exception as e:
        print(f"Warning: Firebase configuration initialization failed: {e}")
        return None


def _str_to_bool(value: str) -> bool:
    """Convert string value to boolean"""
    return value.lower() in ("true", "1", "yes", "on")

# Initialize config at module load time
firebase_config = _initialize_firebase_config()


def reinitialize_firebase_config(load_dotenv_file: bool = True) -> Optional[FirebaseConfig]:
    """
    Reinitialize Firebase configuration (useful for testing)

    Args:
        load_dotenv_file: Whether to load .env file (set to False in tests)

    Returns:
        FirebaseConfig instance or None if initialization fails
    """
    global firebase_config
    firebase_config = _initialize_firebase_config(load_dotenv_file=load_dotenv_file)
    return firebase_config


def get_firebase_config() -> FirebaseConfig:
    """
    Get Firebase configuration instance

    Returns:
        FirebaseConfig: Valid configuration instance

    Raises:
        RuntimeError: If configuration is not available with helpful error message
    """
    if firebase_config is None:
        raise RuntimeError(
            "Firebase configuration is not available. This usually means required "
            "environment variables are missing. Please check your .env file and ensure "
            "FIREBASE_PROJECT_ID is set. For local development, you can also set "
            "FIREBASE_USE_EMULATOR=true or BYPASS_AUTH_IN_DEVELOPMENT=true."
        )
    return firebase_config


def get_firebase_config_safe() -> Optional[FirebaseConfig]:
    """
    Get Firebase configuration instance without raising exceptions

    Returns:
        FirebaseConfig instance or None if not available
    """
    return firebase_config


def validate_firebase_environment(reinitialize: bool = False, load_dotenv_file: bool = True) -> dict:
    """
    Validate Firebase environment configuration with detailed information

    Args:
        reinitialize: If True, force reinitialization of the config (useful for testing)
        load_dotenv_file: Whether to load .env file during reinitialization

    Returns:
        dict: Comprehensive validation results and configuration status
    """
    if reinitialize:
        config = reinitialize_firebase_config(load_dotenv_file=load_dotenv_file)
    else:
        config = get_firebase_config_safe()

    # Check environment variables directly for more reliable validation
    env_project_id = os.getenv("FIREBASE_PROJECT_ID")
    env_use_emulator = _str_to_bool(os.getenv("FIREBASE_USE_EMULATOR", "false"))
    env_bypass_auth = _str_to_bool(os.getenv("BYPASS_AUTH_IN_DEVELOPMENT", "false"))

    if config is None:
        # Provide more specific error details
        missing_vars = []
        if not env_project_id:
            missing_vars.append("FIREBASE_PROJECT_ID")

        error_details = []
        if missing_vars:
            error_details.append(f"Missing required environment variables: {', '.join(missing_vars)}")
        error_details.append("Firebase configuration initialization failed due to Pydantic validation errors")

        return {
            "valid": False,
            "error": (
                "Firebase configuration could not be initialized. Issues found:\n" +
                "\n".join(f"  - {detail}" for detail in error_details) +
                "\n\nPlease check your .env file and ensure required variables are set."
            ),
            "project_id": env_project_id,
            "use_emulator": env_use_emulator,
            "bypass_auth_in_development": env_bypass_auth,
            "configuration_available": False,
            "environment_variables_detected": {
                "FIREBASE_PROJECT_ID": env_project_id,
                "FIREBASE_USE_EMULATOR": os.getenv("FIREBASE_USE_EMULATOR"),
                "BYPASS_AUTH_IN_DEVELOPMENT": os.getenv("BYPASS_AUTH_IN_DEVELOPMENT"),
                "FIREBASE_SERVICE_ACCOUNT_KEY_PATH": os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH"),
                "GOOGLE_APPLICATION_CREDENTIALS": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            },
            "suggestions": [
                "Check if .env file exists and contains FIREBASE_PROJECT_ID",
                "Verify .env file format (no quotes around values unless needed)",
                "For development, consider setting FIREBASE_USE_EMULATOR=true",
                "For testing, you can set BYPASS_AUTH_IN_DEVELOPMENT=true",
                "Check the environment_variables_detected section above for current values"
            ]
        }

    try:
        # Try to validate the configuration
        config.validate_configuration()

        return {
            "valid": True,
            "project_id": config.project_id,
            "use_emulator": config.use_emulator,
            "has_service_account": bool(config.service_account_key_path),
            "has_google_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            "verify_tokens": config.verify_tokens,
            "require_email_verification": config.require_email_verification,
            "auth_emulator_host": config.auth_emulator_host,
            "allow_mock_tokens": config.allow_mock_tokens,
            "bypass_auth_in_development": config.bypass_auth_in_development,
            "configuration_available": True,
            "status": "Configuration is valid and ready for use"
        }

    except ValueError as e:
        return {
            "valid": False,
            "error": str(e),
            "project_id": config.project_id,
            "use_emulator": config.use_emulator,
            "configuration_available": True,
            "has_service_account": bool(config.service_account_key_path),
            "has_google_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            "suggestions": [
                "Review the validation errors above",
                "Check your .env file for required variables",
                "For development, consider using emulator mode",
                "Verify service account credentials path if specified"
            ]
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Unexpected validation error: {str(e)}",
            "project_id": getattr(config, "project_id", None),
            "configuration_available": True,
            "suggestions": [
                "Check logs for detailed error information",
                "Verify environment variable formats",
                "Try reinitializing the configuration"
            ]
        }


def validate_startup_configuration(raise_on_failure: bool = False) -> dict:
    """
    Comprehensive startup configuration validation for Firebase

    This function performs a complete validation of the Firebase configuration
    and provides detailed feedback for troubleshooting startup issues.

    Args:
        raise_on_failure: If True, raises RuntimeError with detailed message on validation failure

    Returns:
        dict: Detailed validation results with suggestions

    Raises:
        RuntimeError: If raise_on_failure=True and validation fails
    """
    import sys
    from pathlib import Path

    # Check if .env file exists
    env_file_path = Path(".env")
    env_file_exists = env_file_path.exists()

    # Get current environment variables
    env_vars = {
        "FIREBASE_PROJECT_ID": os.getenv("FIREBASE_PROJECT_ID"),
        "FIREBASE_USE_EMULATOR": os.getenv("FIREBASE_USE_EMULATOR"),
        "BYPASS_AUTH_IN_DEVELOPMENT": os.getenv("BYPASS_AUTH_IN_DEVELOPMENT"),
        "FIREBASE_SERVICE_ACCOUNT_KEY_PATH": os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH"),
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "FIREBASE_VERIFY_TOKENS": os.getenv("FIREBASE_VERIFY_TOKENS"),
        "FIREBASE_AUTH_EMULATOR_HOST": os.getenv("FIREBASE_AUTH_EMULATOR_HOST")
    }

    # Analyze configuration
    issues = []
    warnings = []
    suggestions = []

    # Check critical environment variables
    if not env_vars["FIREBASE_PROJECT_ID"]:
        issues.append("FIREBASE_PROJECT_ID is not set - this is required for Firebase authentication")
        suggestions.append("Add FIREBASE_PROJECT_ID=your-project-id to your .env file")

    # Check for proper development setup
    use_emulator = _str_to_bool(env_vars["FIREBASE_USE_EMULATOR"] or "false")
    bypass_auth = _str_to_bool(env_vars["BYPASS_AUTH_IN_DEVELOPMENT"] or "false")
    has_service_account = bool(env_vars["FIREBASE_SERVICE_ACCOUNT_KEY_PATH"])
    has_google_creds = bool(env_vars["GOOGLE_APPLICATION_CREDENTIALS"])

    if not use_emulator and not bypass_auth and not has_service_account and not has_google_creds:
        issues.append(
            "No Firebase credentials configured. Need either:\n"
            "  - FIREBASE_USE_EMULATOR=true (for development with emulator)\n"
            "  - BYPASS_AUTH_IN_DEVELOPMENT=true (for development without Firebase)\n"
            "  - FIREBASE_SERVICE_ACCOUNT_KEY_PATH (path to service account JSON)\n"
            "  - GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON)"
        )

    # Check emulator configuration
    if use_emulator and not env_vars["FIREBASE_AUTH_EMULATOR_HOST"]:
        warnings.append("FIREBASE_USE_EMULATOR=true but FIREBASE_AUTH_EMULATOR_HOST not set")
        suggestions.append("Add FIREBASE_AUTH_EMULATOR_HOST=localhost:9099 to your .env file")

    # Check .env file
    if not env_file_exists:
        warnings.append(".env file not found in current directory")
        suggestions.append("Create a .env file based on .env.example template")

    # Test configuration initialization
    config_test_result = validate_firebase_environment(reinitialize=True)

    # Determine overall status
    is_valid = len(issues) == 0 and config_test_result["valid"]

    result = {
        "valid": is_valid,
        "environment_file_exists": env_file_exists,
        "environment_file_path": str(env_file_path.absolute()),
        "current_working_directory": str(Path.cwd()),
        "python_path": sys.executable,
        "environment_variables": env_vars,
        "configuration_analysis": {
            "project_id_set": bool(env_vars["FIREBASE_PROJECT_ID"]),
            "use_emulator": use_emulator,
            "bypass_auth_in_development": bypass_auth,
            "has_service_account_key": has_service_account,
            "has_google_application_credentials": has_google_creds,
            "emulator_host_configured": bool(env_vars["FIREBASE_AUTH_EMULATOR_HOST"])
        },
        "issues": issues,
        "warnings": warnings,
        "suggestions": suggestions,
        "config_initialization_result": config_test_result
    }

    if not is_valid:
        error_message = f"Firebase startup configuration validation failed:\n"
        if issues:
            error_message += "\nCritical Issues:\n"
            error_message += "\n".join(f"  - {issue}" for issue in issues)

        if warnings:
            error_message += "\nWarnings:\n"
            error_message += "\n".join(f"  - {warning}" for warning in warnings)

        if suggestions:
            error_message += "\nSuggestions:\n"
            error_message += "\n".join(f"  - {suggestion}" for suggestion in suggestions)

        result["startup_error_message"] = error_message

        if raise_on_failure:
            raise RuntimeError(error_message)

    return result