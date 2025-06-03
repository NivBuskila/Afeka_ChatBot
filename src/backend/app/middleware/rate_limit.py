# app/middleware/rate_limit.py
"""Rate limiting middleware"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import time
from .base import BaseMiddleware
from app.config import settings


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, app, rate_limit: Optional[int] = None):
        super().__init__(app, rate_limit=rate_limit)
        self.rate_limit = rate_limit or settings.api_rate_limit
        self.rate_limit_data: Dict[str, Dict] = {}
        
        # Paths to skip rate limiting
        self.skip_paths = {
            "/api/health",
            "/",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting"""
        
        # Skip rate limiting for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get current time window
        current_time = time.time()
        minute_window = int(current_time / 60)
        
        # Clean up old entries (older than 2 minutes)
        self._cleanup_old_entries(minute_window)
        
        # Initialize or reset rate limit data for new minute window
        if client_ip not in self.rate_limit_data or \
           self.rate_limit_data[client_ip]["window"] != minute_window:
            self.rate_limit_data[client_ip] = {
                "window": minute_window,
                "count": 0
            }
        
        # Increment request count
        self.rate_limit_data[client_ip]["count"] += 1
        
        # Check if rate limit exceeded
        if self.rate_limit_data[client_ip]["count"] > self.rate_limit:
            self.logger.warning(f"Rate limit exceeded for IP {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Please try again later."},
                headers={
                    "X-RateLimit-Limit": str(self.rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str((minute_window + 1) * 60)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.rate_limit - self.rate_limit_data[client_ip]["count"])
        )
        response.headers["X-RateLimit-Reset"] = str((minute_window + 1) * 60)
        
        return response
    
    def _cleanup_old_entries(self, current_window: int):
        """Remove old entries from rate limit data"""
        # Remove entries older than 2 minutes
        old_window = current_window - 2
        
        # Create a list of IPs to remove (can't modify dict during iteration)
        ips_to_remove = [
            ip for ip, data in self.rate_limit_data.items()
            if data["window"] < old_window
        ]
        
        # Remove old entries
        for ip in ips_to_remove:
            del self.rate_limit_data[ip]
        
        if ips_to_remove:
            self.logger.debug(f"Cleaned up {len(ips_to_remove)} old rate limit entries")