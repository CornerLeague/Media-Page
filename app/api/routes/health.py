"""Health check routes."""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from ..deps import get_redis
from ...services.redis_service import RedisService
from ...core.config import get_settings
from ...models.base import BaseResponse

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, str]
    uptime: str


class DetailedHealthResponse(BaseResponse):
    """Detailed health check response."""

    health: HealthResponse


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic application health status"
)
async def health_check():
    """
    Basic health check endpoint.

    Returns the current status of the application.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        environment="development" if settings.DEBUG else "production",
        services={
            "api": "healthy",
            "redis": "unknown"
        },
        uptime="unknown"
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Returns detailed application health status including service dependencies"
)
async def detailed_health_check(
    redis_service: RedisService = Depends(get_redis)
):
    """
    Detailed health check endpoint.

    Checks the health of all application dependencies:
    - Redis connection
    - Application configuration
    - Service availability
    """
    # Check Redis health
    redis_status = "healthy" if await redis_service.health_check() else "unhealthy"

    # Determine overall status
    overall_status = "healthy" if redis_status == "healthy" else "degraded"

    health_data = HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        environment="development" if settings.DEBUG else "production",
        services={
            "api": "healthy",
            "redis": redis_status
        },
        uptime="unknown"  # TODO: Implement actual uptime tracking
    )

    return DetailedHealthResponse(
        success=True,
        message="Health check completed",
        data=None,
        health=health_data
    )


@router.get(
    "/health/redis",
    status_code=status.HTTP_200_OK,
    summary="Redis health check",
    description="Checks Redis connection health"
)
async def redis_health_check(
    redis_service: RedisService = Depends(get_redis)
):
    """
    Redis-specific health check.

    Tests the Redis connection and returns status.
    """
    is_healthy = await redis_service.health_check()

    return {
        "service": "redis",
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.utcnow(),
        "details": {
            "url": settings.REDIS_URL,
            "db": settings.REDIS_DB
        }
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Kubernetes/Docker readiness probe endpoint"
)
async def readiness_check(
    redis_service: RedisService = Depends(get_redis)
):
    """
    Readiness check for container orchestration.

    This endpoint is used by Kubernetes/Docker to determine
    if the application is ready to receive traffic.
    """
    redis_healthy = await redis_service.health_check()

    if not redis_healthy:
        return {
            "status": "not ready",
            "timestamp": datetime.utcnow(),
            "reason": "Redis connection unhealthy"
        }, status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready",
        "timestamp": datetime.utcnow()
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Kubernetes/Docker liveness probe endpoint"
)
async def liveness_check():
    """
    Liveness check for container orchestration.

    This endpoint is used by Kubernetes/Docker to determine
    if the application is alive and should be restarted if not.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow()
    }