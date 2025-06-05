# app/core/exceptions.py
"""Custom exceptions for the application"""


from typing import Any, Optional


class BaseException(Exception):
    """Base exception class for the application"""
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ServiceException(BaseException):
    """Exception raised by service layer"""
    pass


class RepositoryException(BaseException):
    """Exception raised by repository layer"""
    pass


class ValidationException(BaseException):
    """Exception raised for validation errors"""
    pass


class AuthenticationException(BaseException):
    """Exception raised for authentication errors"""
    pass


class AuthorizationException(BaseException):
    """Exception raised for authorization errors"""
    pass


class NotFoundException(BaseException):
    """Exception raised when a resource is not found"""
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier {identifier} not found"
        super().__init__(message, code="NOT_FOUND")


class ConflictException(BaseException):
    """Exception raised when there's a conflict (e.g., duplicate resource)"""
    pass


class ExternalServiceException(BaseException):
    """Exception raised when external service fails"""
    pass
