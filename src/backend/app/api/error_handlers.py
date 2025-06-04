# app/api/error_handlers.py
"""Centralized error handling for the API"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

from app.schemas.common import ErrorResponse
from app.core.exceptions import (
    ServiceException,
    RepositoryException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    ExternalServiceException
)

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException"""
    logger.warning(
        f"HTTP exception on {request.method} {request.url.path}: "
        f"{exc.status_code} - {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail if isinstance(exc.detail, str) else "Request failed",
            detail=str(exc.detail) if not isinstance(exc.detail, str) else None
        ).dict()
    )


async def starlette_exception_handler(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle Starlette HTTPException"""
    return await http_exception_handler(request, exc)


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors"""
    logger.error(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()}"
    )
    
    # Format validation errors
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            detail={"validation_errors": formatted_errors}
        ).dict()
    )


async def service_exception_handler(
    request: Request, 
    exc: ServiceException
) -> JSONResponse:
    """Handle service layer exceptions"""
    logger.error(
        f"Service exception on {request.method} {request.url.path}: {exc.message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="Service Error",
            detail=exc.message
        ).dict()
    )


async def repository_exception_handler(
    request: Request, 
    exc: RepositoryException
) -> JSONResponse:
    """Handle repository layer exceptions"""
    logger.error(
        f"Repository exception on {request.method} {request.url.path}: {exc.message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Database Error",
            detail="A database error occurred"
        ).dict()
    )


async def not_found_exception_handler(
    request: Request, 
    exc: NotFoundException
) -> JSONResponse:
    """Handle not found exceptions"""
    logger.warning(
        f"Not found exception on {request.method} {request.url.path}: {exc.message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error="Not Found",
            detail=exc.message
        ).dict()
    )


async def authentication_exception_handler(
    request: Request, 
    exc: AuthenticationException
) -> JSONResponse:
    """Handle authentication exceptions"""
    logger.warning(
        f"Authentication exception on {request.method} {request.url.path}: {exc.message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse(
            error="Authentication Failed",
            detail=exc.message
        ).dict(),
        headers={"WWW-Authenticate": "Bearer"}
    )


async def authorization_exception_handler(
    request: Request, 
    exc: AuthorizationException
) -> JSONResponse:
    """Handle authorization exceptions"""
    logger.warning(
        f"Authorization exception on {request.method} {request.url.path}: {exc.message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=ErrorResponse(
            error="Access Denied",
            detail=exc.message
        ).dict()
    )


async def conflict_exception_handler(
    request: Request, 
    exc: ConflictException
) -> JSONResponse:
    """Handle conflict exceptions"""
    logger.warning(
        f"Conflict exception on {request.method} {request.url.path}: {exc.message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorResponse(
            error="Conflict",
            detail=exc.message
        ).dict()
    )


async def external_service_exception_handler(
    request: Request, 
    exc: ExternalServiceException
) -> JSONResponse:
    """Handle external service exceptions"""
    logger.error(
        f"External service exception on {request.method} {request.url.path}: {exc.message}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error="External Service Error",
            detail="An external service is currently unavailable"
        ).dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions"""
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {type(exc).__name__}: {str(exc)}",
        exc_info=True
    )
    
    # Don't expose internal errors in production
    from app.config import settings
    detail = str(exc) if settings.is_development else "An unexpected error occurred"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=detail
        ).dict()
    )


def register_error_handlers(app):
    """Register all error handlers with the FastAPI app"""
    from fastapi import HTTPException
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    
    # FastAPI exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Custom exceptions
    app.add_exception_handler(ServiceException, service_exception_handler)
    app.add_exception_handler(RepositoryException, repository_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)
    app.add_exception_handler(AuthorizationException, authorization_exception_handler)
    app.add_exception_handler(ConflictException, conflict_exception_handler)
    app.add_exception_handler(ExternalServiceException, external_service_exception_handler)
    
    # General exception handler
    app.add_exception_handler(Exception, general_exception_handler)