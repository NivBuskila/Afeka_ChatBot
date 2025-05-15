import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from ..config.settings import settings

logger = logging.getLogger(__name__)

# Rate limiting data store - would be better in Redis for production
rate_limit_data = {}

async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware that implements rate limiting by client IP address.
    
    This prevents abuse by limiting the number of requests a client can
    make within a given time window.
    
    In production, this should use a distributed cache like Redis instead
    of an in-memory dictionary.
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for certain paths (docs, health check, root)
    if request.url.path in [
        settings.DOCS_URL, 
        settings.REDOC_URL, 
        settings.OPENAPI_URL, 
        "/api/health", 
        "/"
    ]:
        return await call_next(request)
    
    # Calculate current minute window
    current_time = time.time()
    minute_window = int(current_time / 60)
    
    # Initialize or reset rate limit data for new minute window
    if client_ip not in rate_limit_data or rate_limit_data[client_ip]["window"] != minute_window:
        rate_limit_data[client_ip] = {"window": minute_window, "count": 0}
    
    # Increment request count for this IP
    rate_limit_data[client_ip]["count"] += 1
    
    # Check if rate limit exceeded
    if rate_limit_data[client_ip]["count"] > settings.API_RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests. Please try again later."}
        )
    
    # Process the request
    response = await call_next(request)
    
    # Add rate limit headers to inform clients
    response.headers["X-RateLimit-Limit"] = str(settings.API_RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(
        max(0, settings.API_RATE_LIMIT - rate_limit_data[client_ip]["count"])
    )
    response.headers["X-RateLimit-Reset"] = str((minute_window + 1) * 60)
    
    return response