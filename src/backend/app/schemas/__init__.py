# app/schemas/__init__.py
"""API schemas (DTOs) for request/response validation"""

from .chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatMessageResponse
)
from .document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse
)
from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    AdminCreate,
    AdminResponse
)
from .common import (
    SuccessResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse
)

__all__ = [
    # Chat
    'ChatRequest',
    'ChatResponse',
    'ChatSessionCreate',
    'ChatSessionUpdate',
    'ChatSessionResponse',
    'ChatMessageResponse',
    # Document
    'DocumentCreate',
    'DocumentUpdate',
    'DocumentResponse',
    'DocumentListResponse',
    # User
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'AdminCreate',
    'AdminResponse',
    # Common
    'SuccessResponse',
    'ErrorResponse',
    'PaginationParams',
    'PaginatedResponse'
]
