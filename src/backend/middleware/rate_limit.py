import time
import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

# Import config using absolute path
from backend.core import config 

logger = logging.getLogger(__name__)

# Use rate limit from config
# API_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT", "100"))  
rate_limit_data = {}

async def rate_limit_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"

    # Skip rate limiting for certain paths
    # Note: Consider making these paths configurable
    if request.url.path in [config.DOCS_URL, config.REDOC_URL, config.OPENAPI_URL, "/api/health", "/"]:
        return await call_next(request)

    current_time = time.time()
    minute_window = int(current_time / 60)

    # Initialize or reset rate limit data for new minute window
    if client_ip not in rate_limit_data or rate_limit_data[client_ip]["window"] != minute_window:
        rate_limit_data[client_ip] = {"window": minute_window, "count": 0}

    # Increment request count for this IP
    rate_limit_data[client_ip]["count"] += 1

    # Check if rate limit exceeded using config value
    if rate_limit_data[client_ip]["count"] > config.API_RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests. Please try again later."}
        )

    # Add rate limit headers using config value
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(config.API_RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(max(0, config.API_RATE_LIMIT - rate_limit_data[client_ip]["count"]))
    response.headers["X-RateLimit-Reset"] = str((minute_window + 1) * 60)

    return response 