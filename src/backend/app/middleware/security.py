import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def add_security_headers(request: Request, call_next):
    """
    Middleware that adds security-related HTTP headers to responses.
    
    These headers help protect against common web vulnerabilities like
    XSS, clickjacking, MIME sniffing, etc.
    """
    # Process the request and get the response
    response = await call_next(request)
    
    # Add security headers
    # Prevent browsers from interpreting files as a different MIME type
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent site from being loaded in an iframe (clickjacking protection)
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable browser's XSS filtering
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Enforce HTTPS for the site and all subdomains
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Control how much referrer information is included with requests
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Content Security Policy could be added here, though it should be configured per application
    # response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response