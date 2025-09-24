"""
Enhanced logging middleware for FastAPI with request context and performance monitoring
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class ContextualLogger:
    """
    Structured logger with request context for better debugging and monitoring
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _format_context(self, request: Request, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format request context for structured logging

        Args:
            request: FastAPI request object
            extra: Additional context data

        Returns:
            Dictionary with structured logging context
        """
        context = {
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else None,
            "user_agent": request.headers.get("user-agent"),
            "client_ip": self._get_client_ip(request),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Add Firebase user context if available
        if hasattr(request.state, "firebase_user"):
            firebase_user = request.state.firebase_user
            if firebase_user:
                context["user_id"] = firebase_user.uid
                context["user_email"] = firebase_user.email
                context["email_verified"] = firebase_user.email_verified

        # Add database user context if available
        if hasattr(request.state, "db_user"):
            db_user = request.state.db_user
            if db_user:
                context["db_user_id"] = str(db_user.id)
                context["onboarded"] = db_user.is_onboarded
                context["current_step"] = db_user.current_onboarding_step

        # Merge any additional context
        if extra:
            context.update(extra)

        return context

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """
        Extract client IP address from request headers

        Args:
            request: FastAPI request object

        Returns:
            Client IP address or None
        """
        # Check for forwarded headers (common with reverse proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to client host
        if request.client:
            return request.client.host

        return None

    def debug(self, request: Request, message: str, **kwargs):
        """Log debug message with request context"""
        context = self._format_context(request, kwargs)
        self.logger.debug(f"{message}", extra={"context": context})

    def info(self, request: Request, message: str, **kwargs):
        """Log info message with request context"""
        context = self._format_context(request, kwargs)
        self.logger.info(f"{message}", extra={"context": context})

    def warning(self, request: Request, message: str, **kwargs):
        """Log warning message with request context"""
        context = self._format_context(request, kwargs)
        self.logger.warning(f"{message}", extra={"context": context})

    def error(self, request: Request, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with request context and exception details"""
        context = self._format_context(request, kwargs)
        if exception:
            context["exception_type"] = type(exception).__name__
            context["exception_message"] = str(exception)

        self.logger.error(f"{message}", extra={"context": context}, exc_info=exception)

    def critical(self, request: Request, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message with request context"""
        context = self._format_context(request, kwargs)
        if exception:
            context["exception_type"] = type(exception).__name__
            context["exception_message"] = str(exception)

        self.logger.critical(f"{message}", extra={"context": context}, exc_info=exception)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring API performance and logging request/response metrics
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = ContextualLogger(__name__)
        self.request_logger = logging.getLogger("api.requests")

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Monitor request performance and log structured request/response data

        Args:
            request: FastAPI request object
            call_next: Next middleware in chain

        Returns:
            Response object with performance monitoring
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Track start time
        start_time = time.time()

        # Log incoming request
        request_size = int(request.headers.get("content-length", 0))

        self.request_logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None,
                "user_agent": request.headers.get("user-agent"),
                "content_length": request_size,
                "client_ip": self._get_client_ip(request),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "request_start"
            }
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log failed requests
            duration_ms = (time.time() - start_time) * 1000

            self.request_logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "client_ip": self._get_client_ip(request),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "event": "request_error"
                },
                exc_info=True
            )
            raise

        # Calculate response time
        duration_ms = (time.time() - start_time) * 1000

        # Determine log level based on response time and status
        log_level = "info"
        if duration_ms > 2000:  # Slow requests (>2s)
            log_level = "warning"
        elif duration_ms > 5000:  # Very slow requests (>5s)
            log_level = "error"
        elif response.status_code >= 500:  # Server errors
            log_level = "error"
        elif response.status_code >= 400:  # Client errors
            log_level = "warning"

        # Log completed request with performance metrics
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "request_size_bytes": request_size,
            "response_size_bytes": len(response.body) if hasattr(response, 'body') else None,
            "client_ip": self._get_client_ip(request),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "request_complete"
        }

        # Add performance categorization
        if duration_ms > 5000:
            log_data["performance"] = "very_slow"
        elif duration_ms > 2000:
            log_data["performance"] = "slow"
        elif duration_ms > 1000:
            log_data["performance"] = "moderate"
        else:
            log_data["performance"] = "fast"

        # Add authentication context if available
        if hasattr(request.state, "firebase_user") and request.state.firebase_user:
            log_data["authenticated"] = True
            log_data["user_id"] = request.state.firebase_user.uid
        else:
            log_data["authenticated"] = False

        # Log with appropriate level
        log_message = f"Request completed: {request.method} {request.url.path} - {response.status_code} ({duration_ms:.1f}ms)"

        if log_level == "error":
            self.request_logger.error(log_message, extra=log_data)
        elif log_level == "warning":
            self.request_logger.warning(log_message, extra=log_data)
        else:
            self.request_logger.info(log_message, extra=log_data)

        # Add response headers for debugging
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"

        return response

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """
        Extract client IP address from request headers

        Args:
            request: FastAPI request object

        Returns:
            Client IP address or None
        """
        # Check for forwarded headers (common with reverse proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return None


class APIEndpointLogger:
    """
    Specialized logger for API endpoints with common logging patterns
    """

    def __init__(self, endpoint_name: str):
        self.endpoint_name = endpoint_name
        self.logger = ContextualLogger(f"api.endpoints.{endpoint_name}")

    def log_endpoint_start(self, request: Request, **kwargs):
        """Log the start of an endpoint execution"""
        self.logger.info(
            request,
            f"Starting {self.endpoint_name} endpoint",
            endpoint=self.endpoint_name,
            event="endpoint_start",
            **kwargs
        )

    def log_endpoint_success(self, request: Request, result_summary: str = None, **kwargs):
        """Log successful endpoint completion"""
        self.logger.info(
            request,
            f"Completed {self.endpoint_name} endpoint successfully" + (f": {result_summary}" if result_summary else ""),
            endpoint=self.endpoint_name,
            event="endpoint_success",
            **kwargs
        )

    def log_endpoint_error(self, request: Request, error: Exception, **kwargs):
        """Log endpoint error"""
        self.logger.error(
            request,
            f"Error in {self.endpoint_name} endpoint: {str(error)}",
            exception=error,
            endpoint=self.endpoint_name,
            event="endpoint_error",
            **kwargs
        )

    def log_validation_error(self, request: Request, validation_details: str, **kwargs):
        """Log validation errors"""
        self.logger.warning(
            request,
            f"Validation error in {self.endpoint_name}: {validation_details}",
            endpoint=self.endpoint_name,
            event="validation_error",
            validation_details=validation_details,
            **kwargs
        )

    def log_business_logic_event(self, request: Request, event: str, details: Dict[str, Any] = None):
        """Log important business logic events"""
        self.logger.info(
            request,
            f"{self.endpoint_name} - {event}",
            endpoint=self.endpoint_name,
            business_event=event,
            event="business_logic",
            **(details or {})
        )

    def log_database_operation(self, request: Request, operation: str, affected_records: int = None, **kwargs):
        """Log database operations"""
        message = f"{self.endpoint_name} - Database {operation}"
        if affected_records is not None:
            message += f" ({affected_records} records)"

        self.logger.debug(
            request,
            message,
            endpoint=self.endpoint_name,
            database_operation=operation,
            affected_records=affected_records,
            event="database_operation",
            **kwargs
        )

    def log_external_service_call(self, request: Request, service: str, operation: str, success: bool, duration_ms: float = None, **kwargs):
        """Log external service calls"""
        status = "success" if success else "failure"
        message = f"{self.endpoint_name} - {service} {operation} {status}"
        if duration_ms:
            message += f" ({duration_ms:.1f}ms)"

        if success:
            self.logger.info(request, message, **kwargs)
        else:
            self.logger.warning(request, message, **kwargs)


def setup_structured_logging():
    """
    Configure structured logging for the application
    """
    # Configure JSON formatter for structured logs in production
    import json
    import logging

    class StructuredFormatter(logging.Formatter):
        """
        Custom formatter that outputs structured JSON logs with context
        """

        def format(self, record):
            # Start with basic log data
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            # Add context if available
            if hasattr(record, 'context'):
                log_data["context"] = record.context

            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)

            # Add any additional fields from extra
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'lineno', 'funcName', 'created',
                              'msecs', 'relativeCreated', 'thread', 'threadName',
                              'processName', 'process', 'message', 'exc_info', 'exc_text',
                              'stack_info', 'context']:
                    log_data[key] = value

            return json.dumps(log_data, default=str)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )

    # Configure specific loggers for structured output
    request_logger = logging.getLogger("api.requests")
    request_logger.setLevel(logging.INFO)

    # Add structured handler for JSON output (useful for production)
    import os
    if os.getenv("ENVIRONMENT") == "production":
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        request_logger.addHandler(handler)

    return request_logger