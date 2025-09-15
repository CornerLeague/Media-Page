"""FastAPI main application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..core.config import get_settings
from ..core.middleware import (
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    RequestSizeLimitMiddleware
)
from ..services.redis_service import get_redis_service, close_redis_service
from .routes import health, auth, users, teams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Corner League Media API...")

    try:
        # Initialize Redis connection
        redis_service = await get_redis_service()
        logger.info("Redis connection established")

        # Store in app state for access in routes
        app.state.redis = redis_service

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Corner League Media API...")

    try:
        # Close Redis connection
        await close_redis_service()
        logger.info("Redis connection closed")

        logger.info("Application shutdown completed successfully")

    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Add middleware
    setup_middleware(app)

    # Add exception handlers
    setup_exception_handlers(app)

    # Include routers
    setup_routes(app)

    return app


def setup_middleware(app: FastAPI):
    """Setup application middleware."""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure as needed for production
        )

    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_size=settings.MAX_REQUEST_SIZE
    )


def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.error(
            f"HTTP {exc.status_code} error at {request.method} {request.url.path}: {exc.detail}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.error(
            f"Validation error at {request.method} {request.url.path}: {exc.errors()}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": exc.errors(),
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(
            f"Unhandled exception at {request.method} {request.url.path}: {str(exc)}",
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "path": str(request.url.path)
            }
        )


def setup_routes(app: FastAPI):
    """Setup application routes."""

    # Health check routes (no prefix)
    app.include_router(
        health.router,
        prefix="",
        tags=["Health"]
    )

    # API v1 routes
    api_prefix = settings.API_V1_STR

    # Authentication routes
    app.include_router(
        auth.router,
        prefix=f"{api_prefix}/auth",
        tags=["Authentication"]
    )

    # User routes
    app.include_router(
        users.router,
        prefix=f"{api_prefix}/users",
        tags=["Users"]
    )

    # Team routes
    app.include_router(
        teams.router,
        prefix=f"{api_prefix}/teams",
        tags=["Teams"]
    )


# Root endpoint
@asynccontextmanager
async def get_app():
    """Get application instance."""
    app = create_application()

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to Corner League Media API",
            "version": settings.VERSION,
            "docs": "/docs" if settings.DEBUG else "Documentation not available in production",
            "health": "/health"
        }

    yield app


# Create application instance
app = create_application()


# Add root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Corner League Media API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production",
        "health": "/health",
        "api_v1": settings.API_V1_STR
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )