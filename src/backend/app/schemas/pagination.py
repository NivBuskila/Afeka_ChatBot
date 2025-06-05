# app/schemas/pagination.py
"""Enhanced pagination schemas for API responses"""

from typing import List, TypeVar, Generic, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from math import ceil

T = TypeVar('T')

class PaginationParams(BaseModel):
    """
    Enhanced pagination parameters for API endpoints
    
    Supports multiple sorting fields and flexible filtering
    """
    page: int = Field(
        default=1, 
        ge=1, 
        description="Page number (1-based indexing)"
    )
    page_size: int = Field(
        default=20, 
        ge=1, 
        le=100, 
        description="Number of items per page (max 100)"
    )
    sort_by: Optional[str] = Field(
        default=None, 
        description="Field to sort by"
    )
    sort_order: str = Field(
        default="desc", 
        description="Sort order: 'asc' or 'desc'"
    )
    search: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Search query for filtering results"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional filters to apply"
    )
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order values"""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('sort_order must be "asc" or "desc"')
        return v.lower()
    
    @validator('search')
    def validate_search(cls, v):
        """Validate search query"""
        if v is not None and not v.strip():
            raise ValueError('Search query cannot be empty')
        return v.strip() if v else None
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size
    
    def to_query_params(self) -> Dict[str, Any]:
        """Convert to query parameters for external APIs"""
        params = {
            "page": self.page,
            "page_size": self.page_size,
            "sort_order": self.sort_order
        }
        
        if self.sort_by:
            params["sort_by"] = self.sort_by
        if self.search:
            params["search"] = self.search
        if self.filters:
            params.update(self.filters)
            
        return params
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "sort_by": "created_at",
                "sort_order": "desc",
                "search": "שעות קבלה",
                "filters": {
                    "is_active": True,
                    "category": "academic"
                }
            }
        }

class PaginationMeta(BaseModel):
    """
    Enhanced pagination metadata with navigation and statistics
    """
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_previous: bool = Field(..., description="Whether there's a previous page")
    
    # Navigation helpers
    next_page: Optional[int] = Field(None, description="Next page number")
    previous_page: Optional[int] = Field(None, description="Previous page number")
    
    # Range information
    start_item: int = Field(..., description="Index of first item on page")
    end_item: int = Field(..., description="Index of last item on page")
    
    # Sorting and filtering info
    sort_by: Optional[str] = Field(None, description="Field used for sorting")
    sort_order: str = Field(..., description="Sort order applied")
    search_query: Optional[str] = Field(None, description="Search query applied")
    filters_applied: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filters that were applied"
    )
    
    @validator('next_page', always=True)
    def calculate_next_page(cls, v, values):
        """Calculate next page number"""
        page = values.get('page', 1)
        total_pages = values.get('total_pages', 0)
        return page + 1 if page < total_pages else None
    
    @validator('previous_page', always=True)
    def calculate_previous_page(cls, v, values):
        """Calculate previous page number"""
        page = values.get('page', 1)
        return page - 1 if page > 1 else None
    
    @validator('start_item', always=True)
    def calculate_start_item(cls, v, values):
        """Calculate start item index"""
        page = values.get('page', 1)
        page_size = values.get('page_size', 20)
        total_items = values.get('total_items', 0)
        
        if total_items == 0:
            return 0
        return ((page - 1) * page_size) + 1
    
    @validator('end_item', always=True)
    def calculate_end_item(cls, v, values):
        """Calculate end item index"""
        page = values.get('page', 1)
        page_size = values.get('page_size', 20)
        total_items = values.get('total_items', 0)
        
        return min(page * page_size, total_items)
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 2,
                "page_size": 20,
                "total_items": 156,
                "total_pages": 8,
                "has_next": True,
                "has_previous": True,
                "next_page": 3,
                "previous_page": 1,
                "start_item": 21,
                "end_item": 40,
                "sort_by": "created_at",
                "sort_order": "desc",
                "search_query": "תקנון",
                "filters_applied": {
                    "is_active": True
                }
            }
        }

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper with enhanced metadata
    """
    items: List[T] = Field(..., description="List of items for current page")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    
    # Summary statistics
    summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional summary statistics about the dataset"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ],
                "meta": {
                    "page": 1,
                    "page_size": 20,
                    "total_items": 2,
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False,
                    "start_item": 1,
                    "end_item": 2,
                    "sort_order": "desc"
                },
                "summary": {
                    "active_items": 2,
                    "inactive_items": 0
                }
            }
        }

class CursorPagination(BaseModel):
    """
    Cursor-based pagination for efficient large dataset traversal
    """
    cursor: Optional[str] = Field(
        None,
        description="Cursor for the next set of results"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items to return"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0wMVQxMjowMDowMFoiLCJpZCI6MTIzfQ==",
                "limit": 20
            }
        }

class CursorPaginatedResponse(BaseModel, Generic[T]):
    """
    Cursor-based paginated response
    """
    items: List[T] = Field(..., description="List of items")
    next_cursor: Optional[str] = Field(
        None,
        description="Cursor for the next page"
    )
    has_more: bool = Field(
        default=False,
        description="Whether there are more items available"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ],
                "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0wMVQxMjowMDowMFoiLCJpZCI6MTI1fQ==",
                "has_more": True
            }
        }

# Helper functions for creating paginated responses

def create_pagination_meta(
    page: int,
    page_size: int,
    total_items: int,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    search_query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> PaginationMeta:
    """
    Create pagination metadata from parameters
    
    Args:
        page: Current page number
        page_size: Items per page
        total_items: Total number of items
        sort_by: Field used for sorting
        sort_order: Sort order
        search_query: Search query applied
        filters: Filters applied
        
    Returns:
        PaginationMeta object
    """
    total_pages = ceil(total_items / page_size) if total_items > 0 else 0
    
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        sort_by=sort_by,
        sort_order=sort_order,
        search_query=search_query,
        filters_applied=filters or {}
    )

def paginate_items(
    items: List[T],
    total_count: int,
    pagination: PaginationParams,
    summary: Optional[Dict[str, Any]] = None
) -> PaginatedResponse[T]:
    """
    Create a paginated response from items and pagination parameters
    
    Args:
        items: List of items for current page
        total_count: Total number of items available
        pagination: Pagination parameters
        summary: Optional summary statistics
        
    Returns:
        PaginatedResponse with items and metadata
    """
    meta = create_pagination_meta(
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_count,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
        search_query=pagination.search,
        filters=pagination.filters
    )
    
    return PaginatedResponse(
        items=items,
        meta=meta,
        summary=summary
    )