"""Common schemas for pagination, filtering, and responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        pagination: PaginationParams,
    ) -> "PaginatedResponse[T]":
        """Create paginated response from items and pagination params."""
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


class ErrorResponse(BaseModel):
    """Standard error response."""

    code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    details: dict | None = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Health status")
    version: str = Field(description="API version")
    environment: str = Field(description="Current environment")
