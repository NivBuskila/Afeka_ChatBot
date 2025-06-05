# app/utils/formatters.py
"""Response formatting utilities"""

from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timezone
import json

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and size_index < len(size_names) - 1:
        size_index += 1
        size /= 1024.0
    
    return f"{size:.1f} {size_names[size_index]}"

def format_datetime(
    dt: datetime,
    format_type: str = "iso",
    timezone_aware: bool = True
) -> str:
    """
    Format datetime for API responses
    
    Args:
        dt: Datetime object to format
        format_type: Format type (iso, display, short)
        timezone_aware: Whether to ensure timezone awareness
        
    Returns:
        Formatted datetime string
    """
    if timezone_aware and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    if format_type == "iso":
        return dt.isoformat()
    elif format_type == "display":
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    elif format_type == "short":
        return dt.strftime("%Y-%m-%d")
    else:
        return dt.isoformat()

def format_response(
    data: Any,
    message: Optional[str] = None,
    status: str = "success",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format standardized API response
    
    Args:
        data: Response data
        message: Optional message
        status: Response status
        metadata: Optional metadata
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "status": status,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    if metadata:
        response["metadata"] = metadata
    
    response["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    return response

def format_error_response(
    error: str,
    details: Optional[Union[str, Dict[str, Any]]] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format standardized error response
    
    Args:
        error: Error message
        details: Error details
        error_code: Optional error code
        
    Returns:
        Formatted error response
    """
    response = {
        "status": "error",
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if details:
        response["details"] = details
    
    if error_code:
        response["error_code"] = error_code
    
    return response

def format_list_response(
    items: List[Any],
    total_count: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Format list response with optional pagination
    
    Args:
        items: List of items
        total_count: Total number of items
        page: Current page number
        page_size: Items per page
        
    Returns:
        Formatted list response
    """
    response = {
        "items": items,
        "count": len(items)
    }
    
    if total_count is not None:
        response["total_count"] = total_count
    
    if page is not None and page_size is not None:
        response["pagination"] = {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if total_count else 0
        }
    
    return format_response(response)

def format_validation_errors(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format validation errors for API response
    
    Args:
        errors: List of validation errors
        
    Returns:
        Formatted validation error response
    """
    formatted_errors = []
    
    for error in errors:
        formatted_error = {
            "field": error.get("loc", ["unknown"])[-1],
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "value_error")
        }
        
        if "input" in error:
            formatted_error["input"] = error["input"]
        
        formatted_errors.append(formatted_error)
    
    return format_error_response(
        error="Validation failed",
        details={"validation_errors": formatted_errors},
        error_code="VALIDATION_ERROR"
    )

def safe_json_serialize(obj: Any) -> str:
    """
    Safely serialize object to JSON
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string
    """
    def json_serializer(obj):
        """Custom JSON serializer for special types"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):  # Pydantic models
            return obj.dict()
        elif hasattr(obj, '__dict__'):  # Regular objects
            return obj.__dict__
        else:
            return str(obj)
    
    try:
        return json.dumps(obj, default=json_serializer, ensure_ascii=False, indent=2)
    except Exception:
        return json.dumps(str(obj))

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 250 - len(ext)
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename or "unnamed_file"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format percentage value
    
    Args:
        value: Percentage value (0.0 to 1.0)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"