# app/middleware/security.py
"""Security headers middleware"""

from fastapi import Request
from .base import BaseMiddleware


class SecurityHeadersMiddleware(BaseMiddleware):
    """Middleware to add security headers to all responses"""
    
    # Default security headers
    DEFAULT_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    
    def __init__(self, app, custom_headers: dict = None):
        super().__init__(app, custom_headers=custom_headers)
        
        # Merge custom headers with defaults
        self.security_headers = {**self.DEFAULT_HEADERS}
        if custom_headers:
            self.security_headers.update(custom_headers)
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to the response"""
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response