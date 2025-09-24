"""
Custom exceptions and error handlers for the API
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.middleware.auth import AuthError
from backend.api.middleware.logging import ContextualLogger

logger = ContextualLogger(__name__)


class APIError(Exception):
    """Base API error class"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(APIError):
    """Validation error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class NotFoundError(APIError):
    """Resource not found error"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier}
        )


class PermissionError(APIError):
    """Permission denied error"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN
        )


class RateLimitError(APIError):
    """Rate limit exceeded error"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ServiceUnavailableError(APIError):
    """Service unavailable error"""

    def __init__(self, service: str, message: Optional[str] = None):
        super().__init__(
            message=message or f"{service} service is currently unavailable",
            error_code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service}
        )


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response

    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        request_id: Request identifier for tracking

    Returns:
        Dict containing standardized error response
    """
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status_code
        }
    }

    if details:
        error_response["error"]["details"] = details

    if request_id:
        error_response["error"]["request_id"] = request_id

    return error_response


async def auth_exception_handler(request: Request, exc: AuthError) -> JSONResponse:
    """
    Handle authentication errors

    Args:
        request: FastAPI request object
        exc: AuthError exception

    Returns:
        JSONResponse with authentication error details
    """
    logger.warning(
        request,
        f"Authentication error: {exc.error_code} - {exc.detail}",
        error_code=exc.error_code,
        error_detail=exc.detail,
        event="authentication_error"
    )

    error_response = create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code,
        details={
            "path": str(request.url.path),
            "method": request.method
        },
        request_id=getattr(request.state, "request_id", None)
    )

    headers = {"WWW-Authenticate": "Bearer"}
    if hasattr(exc, "headers") and exc.headers:
        headers.update(exc.headers)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=headers
    )


async def api_exception_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Handle custom API errors

    Args:
        request: FastAPI request object
        exc: APIError exception

    Returns:
        JSONResponse with API error details
    """
    logger.error(
        request,
        f"API error: {exc.error_code} - {exc.message}",
        exception=exc,
        error_code=exc.error_code,
        error_details=exc.details,
        event="api_error"
    )

    error_response = create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details={
            **exc.details,
            "path": str(request.url.path),
            "method": request.method
        },
        request_id=getattr(request.state, "request_id", None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions

    Args:
        request: FastAPI request object
        exc: HTTP exception

    Returns:
        JSONResponse with HTTP error details
    """
    logger.warning(
        request,
        f"HTTP error: {exc.status_code} - {exc.detail}",
        status_code=exc.status_code,
        error_detail=exc.detail,
        event="http_error"
    )

    # Map HTTP status codes to error codes
    error_code_mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        406: "NOT_ACCEPTABLE",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT",
        410: "GONE",
        413: "PAYLOAD_TOO_LARGE",
        414: "URI_TOO_LONG",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        501: "NOT_IMPLEMENTED",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }

    error_code = error_code_mapping.get(exc.status_code, "HTTP_ERROR")

    error_response = create_error_response(
        error_code=error_code,
        message=exc.detail,
        status_code=exc.status_code,
        details={
            "path": str(request.url.path),
            "method": request.method
        },
        request_id=getattr(request.state, "request_id", None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors

    Args:
        request: FastAPI request object
        exc: Request validation error

    Returns:
        JSONResponse with validation error details
    """
    logger.warning(
        request,
        f"Validation error: {len(exc.errors())} validation issues",
        validation_errors=exc.errors(),
        event="validation_error"
    )

    # Format validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })

    error_response = create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={
            "validation_errors": validation_errors,
            "path": str(request.url.path),
            "method": request.method
        },
        request_id=getattr(request.state, "request_id", None)
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions

    Args:
        request: FastAPI request object
        exc: Generic exception

    Returns:
        JSONResponse with generic error details
    """
    logger.critical(
        request,
        f"Unexpected error: {str(exc)}",
        exception=exc,
        event="unexpected_error"
    )

    error_response = create_error_response(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={
            "path": str(request.url.path),
            "method": request.method
        },
        request_id=getattr(request.state, "request_id", None)
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with FastAPI app

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(AuthError, auth_exception_handler)
    app.add_exception_handler(APIError, api_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)