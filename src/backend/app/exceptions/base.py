# app/exceptions/base.py
"""Base exception classes for the application"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone

class BaseApplicationError(Exception):
    """
    Base exception class for all application errors
    
    Provides:
    - Error code system
    - Detailed error context
    - Timestamp tracking
    - Serialization support
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize base application error
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        """String representation of the error"""
        return f"{self.__class__.__name__}: {self.message}"
    
    def __repr__(self) -> str:
        """Detailed representation of the error"""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"details={self.details})"
        )

class BusinessLogicError(BaseApplicationError):
    """
    Exception for business logic violations
    
    Used when business rules are violated or
    domain constraints are not met
    """
    
    def __init__(
        self,
        message: str,
        rule_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize business logic error
        
        Args:
            message: Description of the business rule violation
            rule_name: Name of the violated business rule
            **kwargs: Additional arguments for BaseApplicationError
        """
        details = kwargs.get('details', {})
        if rule_name:
            details['violated_rule'] = rule_name
        
        super().__init__(
            message=message,
            error_code=kwargs.get('error_code', 'BUSINESS_RULE_VIOLATION'),
            details=details,
            cause=kwargs.get('cause')
        )

class ValidationError(BaseApplicationError):
    """
    Exception for input validation errors
    
    Used when user input doesn't meet validation requirements
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize validation error
        
        Args:
            message: Description of the validation failure
            field_name: Name of the field that failed validation
            field_value: Value that failed validation
            **kwargs: Additional arguments for BaseApplicationError
        """
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if field_value is not None:
            details['field_value'] = str(field_value)
        
        super().__init__(
            message=message,
            error_code=kwargs.get('error_code', 'VALIDATION_ERROR'),
            details=details,
            cause=kwargs.get('cause')
        )

class AuthenticationError(BaseApplicationError):
    """
    Exception for authentication failures
    
    Used when user authentication fails
    """
    
    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=kwargs.get('error_code', 'AUTHENTICATION_FAILED'),
            details=kwargs.get('details', {}),
            cause=kwargs.get('cause')
        )

class AuthorizationError(BaseApplicationError):
    """
    Exception for authorization failures
    
    Used when user lacks required permissions
    """
    
    def __init__(
        self,
        message: str = "Access denied",
        required_permission: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize authorization error
        
        Args:
            message: Description of the authorization failure
            required_permission: Permission that was required
            **kwargs: Additional arguments for BaseApplicationError
        """
        details = kwargs.get('details', {})
        if required_permission:
            details['required_permission'] = required_permission
        
        super().__init__(
            message=message,
            error_code=kwargs.get('error_code', 'ACCESS_DENIED'),
            details=details,
            cause=kwargs.get('cause')
        )

class ResourceNotFoundError(BaseApplicationError):
    """
    Exception for resource not found errors
    
    Used when requested resource doesn't exist
    """
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize resource not found error
        
        Args:
            message: Description of what wasn't found
            resource_type: Type of resource (e.g., "Document", "User")
            resource_id: ID of the resource that wasn't found
            **kwargs: Additional arguments for BaseApplicationError
        """
        details = kwargs.get('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = str(resource_id)
        
        super().__init__(
            message=message,
            error_code=kwargs.get('error_code', 'RESOURCE_NOT_FOUND'),
            details=details,
            cause=kwargs.get('cause')
        )

class ResourceConflictError(BaseApplicationError):
    """
    Exception for resource conflict errors
    
    Used when resource state conflicts prevent operation
    """
    
    def __init__(
        self,
        message: str = "Resource conflict",
        conflict_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize resource conflict error
        
        Args:
            message: Description of the conflict
            conflict_type: Type of conflict (e.g., "duplicate", "state_mismatch")
            **kwargs: Additional arguments for BaseApplicationError
        """
        details = kwargs.get('details', {})
        if conflict_type:
            details['conflict_type'] = conflict_type
        
        super().__init__(
            message=message,
            error_code=kwargs.get('error_code', 'RESOURCE_CONFLICT'),
            details=details,
            cause=kwargs.get('cause')
        )

class ExternalServiceError(BaseApplicationError):
    """
    Exception for external service errors
    
    Used when external service calls fail
    """
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize external service error
        
        Args:
            message: Description of the service error
            service_name: Name of the external service
            status_code: HTTP status code from the service
            **kwargs: Additional arguments for BaseApplicationError
        """
        details = kwargs.get('details', {})
        if service_name:
            details['service_name'] = service_name
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(
            message=message,
            error_code=kwargs.get('error_code', 'EXTERNAL_SERVICE_ERROR'),
            details=details,
            cause=kwargs.get('cause')
        )

# Helper functions for common error scenarios

def not_found(resource_type: str, resource_id: Any) -> ResourceNotFoundError:
    """Create a standard 'not found' error"""
    return ResourceNotFoundError(
        message=f"{resource_type} with ID '{resource_id}' not found",
        resource_type=resource_type,
        resource_id=str(resource_id)
    )

def validation_failed(field_name: str, message: str, value: Any = None) -> ValidationError:
    """Create a standard validation error"""
    return ValidationError(
        message=f"Validation failed for field '{field_name}': {message}",
        field_name=field_name,
        field_value=value
    )

def business_rule_violated(rule_name: str, message: str) -> BusinessLogicError:
    """Create a standard business rule violation error"""
    return BusinessLogicError(
        message=message,
        rule_name=rule_name
    )

def access_denied(required_permission: str = None) -> AuthorizationError:
    """Create a standard access denied error"""
    message = "Access denied"
    if required_permission:
        message += f": requires '{required_permission}' permission"
    
    return AuthorizationError(
        message=message,
        required_permission=required_permission
    )

def service_unavailable(service_name: str) -> ExternalServiceError:
    """Create a standard service unavailable error"""
    return ExternalServiceError(
        message=f"Service '{service_name}' is currently unavailable",
        service_name=service_name
    )