# app/utils/pagination.py
"""Pagination utilities for API responses"""

from typing import List, TypeVar, Generic, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from math import ceil

T = TypeVar('T')

class PaginationParams(BaseModel):
    """
    Standard pagination parameters for API endpoints
    """
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", description="Sort order: asc or desc")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order values"""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('sort_order must be "asc" or "desc"')
        return v.lower()
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size

class PaginationMeta(BaseModel):
    """
    Pagination metadata for responses
    """
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    sort_by: Optional[str]
    sort_order: str

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper
    """
    items: List[T]
    meta: PaginationMeta

def paginate_query_result(
    items: List[T],
    total_count: int,
    pagination: PaginationParams
) -> PaginatedResponse[T]:
    """
    Create a paginated response from query results
    
    Args:
        items: List of items for current page
        total_count: Total number of items available
        pagination: Pagination parameters used
        
    Returns:
        PaginatedResponse with items and metadata
    """
    total_pages = ceil(total_count / pagination.page_size) if total_count > 0 else 0
    
    meta = PaginationMeta(
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_count,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_previous=pagination.page > 1,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order
    )
    
    return PaginatedResponse(items=items, meta=meta)

def calculate_pagination_info(
    total_items: int,
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Calculate pagination information
    
    Args:
        total_items: Total number of items
        page: Current page number
        page_size: Items per page
        
    Returns:
        Dictionary with pagination info
    """
    total_pages = ceil(total_items / page_size) if total_items > 0 else 0
    
    return {
        "current_page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "start_item": ((page - 1) * page_size) + 1 if total_items > 0 else 0,
        "end_item": min(page * page_size, total_items)
    }

def validate_pagination_params(
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> PaginationParams:
    """
    Validate and normalize pagination parameters
    
    Args:
        page: Page number
        page_size: Items per page
        
    Returns:
        Validated PaginationParams object
    """
    return PaginationParams(
        page=page or 1,
        page_size=min(page_size or 20, 100)  # Max 100 items per page
    )