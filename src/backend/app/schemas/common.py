# app/schemas/common.py
"""Common API schemas"""

from typing import Optional, List, TypeVar, Generic
from pydantic import Field
from .base import BaseSchema

T = TypeVar('T')


class SuccessResponse(BaseSchema):
    """Generic success response"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 1}
            }
        }


class ErrorResponse(BaseSchema):
    """Generic error response"""
    error: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Bad Request",
                "detail": "Invalid input data"
            }
        }


class PaginationParams(BaseSchema):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database query"""
        return self.page_size


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, pagination: PaginationParams):
        """Create paginated response"""
        pages = (total + pagination.page_size - 1) // pagination.page_size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages
        )