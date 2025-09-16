"""Application configuration and settings."""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # Application
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Corner League Media API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI backend for Corner League Media sports platform"
    DEBUG: bool = True  # Set to True for development

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    FRONTEND_URL: str = "http://localhost:8080"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:8082",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8082",
        "http://127.0.0.1:3000"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Clerk Authentication
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_ISSUER: str = "https://clerk.dev"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # API Configuration
    API_TIMEOUT: int = 30  # seconds
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

    @validator("CLERK_SECRET_KEY", pre=True)
    def validate_clerk_secret(cls, v):
        if not v:
            # Allow empty in development, but warn
            import warnings
            warnings.warn("CLERK_SECRET_KEY is not set. Authentication will not work.")
        return v


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings