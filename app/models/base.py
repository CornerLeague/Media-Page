"""Base model classes and utilities."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, validator
import uuid


class BaseModelConfig:
    """Base configuration for all Pydantic models."""

    # Use enum values instead of enum objects
    use_enum_values = True

    # Validate assignment
    validate_assignment = True

    # Allow population by field name
    populate_by_name = True

    # JSON encoders for common types
    json_encoders = {
        datetime: lambda v: v.isoformat(),
        uuid.UUID: lambda v: str(v)
    }


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config(BaseModelConfig):
        pass


class TimestampedSchema(BaseSchema):
    """Base schema with timestamp fields."""

    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v):
        return v or datetime.utcnow()


class BaseResponse(BaseSchema):
    """Base response model."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseSchema):
    """Error response model."""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseResponse):
    """Paginated response model."""

    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    @validator('total_pages', pre=True, always=True)
    def calculate_total_pages(cls, v, values):
        if 'total_items' in values and 'page_size' in values:
            page_size = values['page_size']
            total_items = values['total_items']
            return (total_items + page_size - 1) // page_size if page_size > 0 else 0
        return v

    @validator('has_next', pre=True, always=True)
    def calculate_has_next(cls, v, values):
        if 'page' in values and 'total_pages' in values:
            return values['page'] < values['total_pages']
        return False

    @validator('has_prev', pre=True, always=True)
    def calculate_has_prev(cls, v, values):
        if 'page' in values:
            return values['page'] > 1
        return False