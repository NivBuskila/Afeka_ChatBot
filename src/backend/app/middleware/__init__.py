# app/middleware/__init__.py
"""Middleware components for the Afeka ChatBot API"""

from .cors import setup_cors
from .rate_limit import RateLimitMiddleware
from .security import SecurityHeadersMiddleware
from .timing import TimingMiddleware
from .trusted_host import setup_trusted_host

__all__ = [
    'setup_cors',
    'RateLimitMiddleware',
    'SecurityHeadersMiddleware',
    'TimingMiddleware',
    'setup_trusted_host'
]