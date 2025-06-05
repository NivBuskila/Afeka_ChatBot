# app/api/request_handlers.py
"""Request preprocessing and response postprocessing handlers"""

from fastapi import Request, Response
from typing import Callable
import json
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


async def log_request_body(request: Request, call_next: Callable) -> Response:
    """Log request body for debugging (development only)"""
    from app.config import settings
    
    if not settings.is_development:
        return await call_next(request)
    
    # Skip for GET requests and specific paths
    if request.method == "GET" or request.url.path.startswith("/docs"):
        return await call_next(request)
    
    # Read and log body
    body = await request.body()
    if body:
        try:
            body_str = body.decode('utf-8')
            logger.debug(f"Request body for {request.method} {request.url.path}: {body_str[:500]}")
        except:
            logger.debug(f"Non-UTF8 request body for {request.method} {request.url.path}")
    
    # Important: Return the body to the request
    async def receive():
        return {"type": "http.request", "body": body}
    
    request._receive = receive
    
    return await call_next(request)


async def add_request_id(request: Request, call_next: Callable) -> Response:
    """Add unique request ID to each request for tracing"""
    request_id = str(uuid.uuid4())
    
    # Add to request state
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Add to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


async def handle_options_requests(request: Request, call_next: Callable) -> Response:
    """Handle OPTIONS requests for CORS preflight"""
    if request.method == "OPTIONS":
        return Response(
            content="",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600"
            }
        )
    
    return await call_next(request)


async def cleanup_response_headers(request: Request, call_next: Callable) -> Response:
    """Clean up sensitive headers from responses"""
    response = await call_next(request)
    
    # Remove potentially sensitive headers
    sensitive_headers = ["X-Powered-By", "Server"]
    for header in sensitive_headers:
        if header in response.headers:
            del response.headers[header]
    
    return response