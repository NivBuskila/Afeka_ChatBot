# app/middleware/timing.py
"""Request timing middleware"""

from fastapi import Request
import time
from .base import BaseMiddleware


class TimingMiddleware(BaseMiddleware):
    """Middleware to measure and report request processing time"""
    
    def __init__(self, app, header_name: str = "X-Process-Time"):
        super().__init__(app, header_name=header_name)
        self.header_name = header_name
    
    async def dispatch(self, request: Request, call_next):
        """Measure request processing time and add it to response headers"""
        
        # Record start time
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add header with processing time
        response.headers[self.header_name] = f"{process_time:.3f}"
        
        # Log slow requests (over 1 second)
        if process_time > 1.0:
            self.logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.3f} seconds"
            )
        
        return response