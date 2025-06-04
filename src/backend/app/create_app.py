# app/create_app.py
"""Application factory for creating the FastAPI app"""

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from app.config import settings
from app.core.logging import setup_logging
from app.middleware import (
    setup_cors,
    setup_trusted_host,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    TimingMiddleware
)
from app.api.error_handlers import register_error_handlers
from app.api.request_handlers import (
    add_request_id,
    handle_options_requests,
    cleanup_response_headers,
    log_request_body
)
from app.api.v1 import api_router
from app.api.v1.proxy import router as proxy_router_direct
import logging
from app.api.lifecycle import register_lifecycle_handlers

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Setup logging first
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,  # Disable in production
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None
    )
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add middleware in correct order (last added = first executed)
    
    # Request handlers
    app.middleware("http")(cleanup_response_headers)
    app.middleware("http")(add_request_id)
    app.middleware("http")(handle_options_requests)
    
    if settings.is_development:
        app.middleware("http")(log_request_body)
    
    # Security and performance middleware
    app.add_middleware(TimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, rate_limit=settings.api_rate_limit)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # CORS and trusted host
    setup_cors(app)
    setup_trusted_host(app)
    
    # Include routers
    app.include_router(api_router)
    
    # Legacy support: Mount proxy routes directly under /api
    app.include_router(
        proxy_router_direct,
        prefix="/api",
        tags=["proxy-legacy"]
    )
    
    # Add root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint"""
        return {
            "message": settings.app_name,
            "version": settings.app_version,
            "docs_url": "/docs" if settings.is_development else None
        }
    
    # Legacy redirects
    @app.get("/api/health", tags=["legacy"])
    async def legacy_health():
        """Legacy health endpoint"""
        return {"status": "healthy", "service": settings.app_name}
    
    # Log successful initialization
    logger.info(f"{settings.app_name} v{settings.app_version} initialized successfully")
    
    # Register lifecycle handlers
    register_lifecycle_handlers(app)

    return app


def init_dependencies(app: FastAPI) -> None:
    """Initialize application dependencies"""
    from supabase import create_client
    from app.repositories.factory import init_repository_factory
    from app.services.factory import init_service_factory
    
    # Initialize Supabase client
    supabase_client = None
    try:
        supabase_key = settings.get_supabase_key_value
        if settings.supabase_url and supabase_key:
            supabase_client = create_client(settings.supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
        else:
            logger.warning("Supabase configuration missing - running in degraded mode")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        logger.warning("Running in degraded mode without database")
    
    # Initialize factories
    repository_factory = init_repository_factory(supabase_client)
    service_factory = init_service_factory(repository_factory)
    
    # Store in app state for access in endpoints
    app.state.repository_factory = repository_factory
    app.state.service_factory = service_factory
    app.state.supabase_client = supabase_client
    
    logger.info("Dependencies initialized successfully")