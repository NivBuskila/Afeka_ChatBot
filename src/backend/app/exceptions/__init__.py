# app/exceptions/__init__.py
"""Custom exception classes for the application"""

from .base import (
    BaseApplicationError,
    BusinessLogicError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ResourceConflictError,
    ExternalServiceError
)

__all__ = [
    'BaseApplicationError',
    'BusinessLogicError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'ResourceNotFoundError',
    'ResourceConflictError',
    'ExternalServiceError'
]