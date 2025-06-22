"""Common type imports to prevent duplication across the codebase."""

from typing import (
    Dict, 
    Any, 
    List, 
    Optional, 
    Union, 
    Tuple, 
    Set,
    TypeVar,
    Generic,
    Callable,
    Awaitable,
    AsyncGenerator,
    cast
)
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field

# Export all for easy import
__all__ = [
    'Dict', 'Any', 'List', 'Optional', 'Union', 'Tuple', 'Set',
    'TypeVar', 'Generic', 'Callable', 'Awaitable', 'AsyncGenerator',
    'cast', 'datetime', 'date', 'timedelta', 'BaseModel', 'Field'
]

# Common type aliases
JsonDict = Dict[str, Any]
JsonList = List[Dict[str, Any]]
ID = Union[str, int] 