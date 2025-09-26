"""
Validation middleware for standardizing error response formats
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api.middleware.logging import ContextualLogger

logger = ContextualLogger(__name__)


class ValidationResponseMiddleware(BaseHTTPMiddleware):
    """
    Middleware to standardize validation error responses across all endpoints

    This middleware ensures consistent error response structure for:
    - Pydantic validation errors
    - FastAPI request validation errors
    - Custom validation errors from business logic
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and standardize validation error responses

        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint function

        Returns:
            Response with standardized error format if validation fails
        """
        try:
            response = await call_next(request)
            return response
        except (RequestValidationError, ValidationError) as exc:
            return await self._handle_validation_error(request, exc)
        except Exception:
            # Let other exceptions pass through to the main exception handlers
            raise

    async def _handle_validation_error(
        self,
        request: Request,
        exc: Union[RequestValidationError, ValidationError]
    ) -> JSONResponse:
        """
        Handle validation errors with standardized response format

        Args:
            request: FastAPI request object
            exc: Validation error exception

        Returns:
            JSONResponse with standardized validation error format
        """
        logger.warning(
            request,
            f"Validation error: {type(exc).__name__} with {len(exc.errors())} validation issues",
            validation_errors=exc.errors(),
            event="validation_middleware_error"
        )

        standardized_response = create_standardized_validation_error_response(
            request=request,
            validation_errors=exc.errors(),
            request_id=getattr(request.state, "request_id", None)
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=standardized_response
        )


def create_standardized_validation_error_response(
    request: Request,
    validation_errors: List[Dict[str, Any]],
    request_id: Optional[str] = None,
    custom_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized validation error response

    Args:
        request: FastAPI request object
        validation_errors: List of validation errors from Pydantic
        request_id: Optional request identifier for tracking
        custom_message: Optional custom error message

    Returns:
        Dict containing standardized validation error response
    """
    # Process and categorize validation errors
    processed_errors = []
    field_errors = {}

    for error in validation_errors:
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_type = error["type"]
        error_message = error["msg"]
        invalid_input = error.get("input")

        # Create detailed field error
        field_error = {
            "field": field_path,
            "message": error_message,
            "type": error_type,
            "rejected_value": invalid_input
        }

        # Add contextual information based on error type
        if error_type == "value_error.uuid.invalid":
            field_error["expected_format"] = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            field_error["examples"] = [
                "2350948d-f6d4-4a85-9358-b76ed505aea2",
                "498127a1-e061-4386-89ce-a5f00692004c"
            ]
        elif error_type == "type_error.str":
            field_error["expected_type"] = "string"
        elif error_type == "type_error.list":
            field_error["expected_type"] = "array"
        elif error_type == "value_error.missing":
            field_error["suggestion"] = f"Please provide a value for '{field_path}'"
        elif "enum" in error_type:
            # Extract allowed values from error context if available
            if "permitted" in error.get("ctx", {}):
                field_error["allowed_values"] = error["ctx"]["permitted"]

        processed_errors.append(field_error)

        # Group errors by field for easier frontend handling
        field_name = field_path.split(" -> ")[-1]  # Get the last part of the field path
        if field_name not in field_errors:
            field_errors[field_name] = []
        field_errors[field_name].append(field_error)

    # Determine the most appropriate general error message
    if custom_message:
        general_message = custom_message
    elif len(processed_errors) == 1:
        general_message = f"Validation failed for field '{processed_errors[0]['field']}'"
    else:
        general_message = f"Validation failed for {len(processed_errors)} fields"

    # Create standardized response structure
    error_response = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": general_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": {
                "path": str(request.url.path),
                "method": request.method,
                "validation_errors": processed_errors,
                "field_errors": field_errors,
                "error_count": len(processed_errors)
            }
        }
    }

    if request_id:
        error_response["error"]["request_id"] = request_id

    return error_response


def create_business_logic_validation_error_response(
    request: Request,
    field_name: str,
    error_message: str,
    invalid_value: Any = None,
    suggestions: Optional[List[str]] = None,
    error_code: str = "BUSINESS_LOGIC_VALIDATION_ERROR",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized validation error response for business logic validation errors

    This function is used by endpoint handlers to create consistent error responses
    for validation errors that occur in business logic (not Pydantic model validation)

    Args:
        request: FastAPI request object
        field_name: Name of the field that failed validation
        error_message: Human-readable error message
        invalid_value: The value that failed validation
        suggestions: List of corrective actions or suggestions
        error_code: Specific error code for this validation failure
        request_id: Optional request identifier for tracking

    Returns:
        Dict containing standardized validation error response
    """
    field_error = {
        "field": field_name,
        "message": error_message,
        "type": "business_logic_validation",
        "rejected_value": invalid_value
    }

    if suggestions:
        field_error["suggestions"] = suggestions

    error_response = {
        "error": {
            "code": error_code,
            "message": f"Validation failed for field '{field_name}'",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": {
                "path": str(request.url.path),
                "method": request.method,
                "validation_errors": [field_error],
                "field_errors": {field_name: [field_error]},
                "error_count": 1
            }
        }
    }

    if request_id:
        error_response["error"]["request_id"] = request_id

    return error_response


def create_multi_field_validation_error_response(
    request: Request,
    field_errors: Dict[str, List[Dict[str, Any]]],
    general_message: Optional[str] = None,
    error_code: str = "MULTI_FIELD_VALIDATION_ERROR",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized validation error response for multiple field validation errors

    Args:
        request: FastAPI request object
        field_errors: Dictionary mapping field names to lists of error details
        general_message: Optional general error message
        error_code: Specific error code for this validation failure
        request_id: Optional request identifier for tracking

    Returns:
        Dict containing standardized validation error response
    """
    # Flatten field errors for the validation_errors array
    processed_errors = []
    for field_name, errors in field_errors.items():
        processed_errors.extend(errors)

    if not general_message:
        error_count = len(processed_errors)
        if error_count == 1:
            general_message = f"Validation failed for field '{processed_errors[0]['field']}'"
        else:
            general_message = f"Validation failed for {error_count} fields"

    error_response = {
        "error": {
            "code": error_code,
            "message": general_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": {
                "path": str(request.url.path),
                "method": request.method,
                "validation_errors": processed_errors,
                "field_errors": field_errors,
                "error_count": len(processed_errors)
            }
        }
    }

    if request_id:
        error_response["error"]["request_id"] = request_id

    return error_response