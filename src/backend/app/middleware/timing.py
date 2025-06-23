import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def add_process_time_header(request: Request, call_next):
    """
    Middleware that adds processing time information to response headers.
    
    This helps with performance monitoring and diagnostics.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log if request takes too long (optional)
    if process_time > 2.0:  # Increased threshold to 2 seconds
        logger.warning(f"Slow request: {request.url.path} took {process_time:.4f}s")
        
    return response