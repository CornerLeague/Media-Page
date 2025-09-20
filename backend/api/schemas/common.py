"""
Common schemas for API responses and pagination
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    data: T
    message: Optional[str] = None
    status: str = Field(default="success", pattern="^(success|error)$")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema"""
    items: List[T]
    total: int = Field(ge=0, description="Total number of items")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Number of items per page")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response with calculated fields"""
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total,
            has_previous=page > 1
        )


class BaseSchema(BaseModel):
    """Base schema with common configuration"""

    class Config:
        # Use enum values instead of enum names
        use_enum_values = True
        # Allow population by field name or alias
        allow_population_by_field_name = True
        # JSON encoders for common types
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields"""
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IDMixin(BaseModel):
    """Mixin for UUID ID field"""
    id: UUID

    class Config:
        json_encoders = {
            UUID: str
        }