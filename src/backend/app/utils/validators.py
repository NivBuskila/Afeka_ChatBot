# app/utils/validators.py
"""Custom validation utilities"""

import re
import uuid
from typing import Optional, List, Any
from datetime import datetime
import mimetypes

from app.exceptions.base import ValidationError

# Regex patterns
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)
PHONE_PATTERN = re.compile(
    r'^\+?[1-9]\d{1,14}$'  # International phone number format
)

# File type configurations
ALLOWED_DOCUMENT_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/csv'
}

ALLOWED_IMAGE_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
}

# File size limits (in bytes)
MAX_DOCUMENT_SIZE = 100 * 1024 * 1024  # 100MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10MB

def validate_uuid(value: str, field_name: str = "UUID") -> str:
    """
    Validate UUID format
    
    Args:
        value: String to validate as UUID
        field_name: Name of the field for error messages
        
    Returns:
        Validated UUID string
        
    Raises:
        ValidationError: If UUID format is invalid
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")
    
    if not UUID_PATTERN.match(value):
        raise ValidationError(f"Invalid {field_name} format")
    
    return value

def validate_email(email: str) -> str:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        Validated email address
        
    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError("Email cannot be empty")
    
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email format")
    
    return email.lower()

def validate_phone(phone: str) -> str:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Validated phone number
        
    Raises:
        ValidationError: If phone format is invalid
    """
    if not phone:
        raise ValidationError("Phone number cannot be empty")
    
    # Remove spaces and dashes for validation
    cleaned_phone = re.sub(r'[\s-]', '', phone)
    
    if not PHONE_PATTERN.match(cleaned_phone):
        raise ValidationError("Invalid phone number format")
    
    return cleaned_phone

def validate_file_type(
    file_type: str, 
    allowed_types: Optional[List[str]] = None,
    category: str = "document"
) -> str:
    """
    Validate file MIME type
    
    Args:
        file_type: MIME type to validate
        allowed_types: Custom list of allowed types
        category: File category (document, image)
        
    Returns:
        Validated file type
        
    Raises:
        ValidationError: If file type is not allowed
    """
    if not file_type:
        raise ValidationError("File type cannot be empty")
    
    if allowed_types:
        valid_types = set(allowed_types)
    elif category == "image":
        valid_types = ALLOWED_IMAGE_TYPES
    else:
        valid_types = ALLOWED_DOCUMENT_TYPES
    
    if file_type not in valid_types:
        raise ValidationError(
            f"Invalid file type '{file_type}'. "
            f"Allowed types: {', '.join(sorted(valid_types))}"
        )
    
    return file_type

def validate_file_size(
    size: int, 
    max_size: Optional[int] = None,
    file_type: Optional[str] = None
) -> int:
    """
    Validate file size
    
    Args:
        size: File size in bytes
        max_size: Custom maximum size
        file_type: MIME type for determining default max size
        
    Returns:
        Validated file size
        
    Raises:
        ValidationError: If file size exceeds limits
    """
    if size <= 0:
        raise ValidationError("File size must be positive")
    
    if max_size:
        limit = max_size
    elif file_type and file_type in ALLOWED_IMAGE_TYPES:
        limit = MAX_IMAGE_SIZE
    else:
        limit = MAX_DOCUMENT_SIZE
    
    if size > limit:
        limit_mb = limit / (1024 * 1024)
        size_mb = size / (1024 * 1024)
        raise ValidationError(
            f"File size ({size_mb:.1f}MB) exceeds limit ({limit_mb:.1f}MB)"
        )
    
    return size

def validate_string_length(
    value: str,
    field_name: str,
    min_length: int = 0,
    max_length: int = 1000
) -> str:
    """
    Validate string length
    
    Args:
        value: String to validate
        field_name: Field name for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Validated string
        
    Raises:
        ValidationError: If string length is invalid
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters long"
        )
    
    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} must be no more than {max_length} characters long"
        )
    
    return value

def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    field_name: str = "Date range"
) -> tuple[datetime, datetime]:
    """
    Validate date range
    
    Args:
        start_date: Start date
        end_date: End date
        field_name: Field name for error messages
        
    Returns:
        Tuple of validated dates
        
    Raises:
        ValidationError: If date range is invalid
    """
    if start_date >= end_date:
        raise ValidationError(f"{field_name}: start date must be before end date")
    
    return start_date, end_date

def validate_positive_number(
    value: Any,
    field_name: str,
    allow_zero: bool = False
) -> float:
    """
    Validate positive number
    
    Args:
        value: Value to validate
        field_name: Field name for error messages
        allow_zero: Whether to allow zero values
        
    Returns:
        Validated number
        
    Raises:
        ValidationError: If number is not positive
    """
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")
    
    if allow_zero and num_value < 0:
        raise ValidationError(f"{field_name} must be non-negative")
    elif not allow_zero and num_value <= 0:
        raise ValidationError(f"{field_name} must be positive")
    
    return num_value

def validate_choice(
    value: str,
    choices: List[str],
    field_name: str,
    case_sensitive: bool = True
) -> str:
    """
    Validate value is in allowed choices
    
    Args:
        value: Value to validate
        choices: List of allowed choices
        field_name: Field name for error messages
        case_sensitive: Whether comparison is case sensitive
        
    Returns:
        Validated choice value
        
    Raises:
        ValidationError: If value is not in choices
    """
    if not case_sensitive:
        value = value.lower()
        choices = [choice.lower() for choice in choices]
    
    if value not in choices:
        raise ValidationError(
            f"Invalid {field_name}. Must be one of: {', '.join(choices)}"
        )
    
    return value