import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from ..config.settings import settings
from ..middleware.timing import add_process_time_header
from ..middleware.security import add_security_headers
from ..middleware.rate_limit import rate_limit_middleware
from ..api.routes import general, chat, documents, proxy
from ...api import vector_management
from ..api.routes.rag import router as rag_router
from ..api.routes.title_generation import router as title_router  
from ..api.routes.api_keys import router as api_keys_router

logger = logging.getLogger(__name__)

class Application:
    """Application factory class for FastAPI setup."""
    
    def __init__(self):
        """Initialize the FastAPI application with all configurations."""
        self.app = FastAPI(
            title=settings.API_TITLE,
            description=settings.API_DESCRIPTION,
            version=settings.API_VERSION,
            docs_url=settings.DOCS_URL,
            redoc_url=settings.REDOC_URL,
            openapi_url=settings.OPENAPI_URL
        )
        self._configure_middleware()
        self._configure_routers()
        self._configure_exception_handlers()
        
        logger.info(f"Application initialized with environment: {settings.ENVIRONMENT}")
    
    def _configure_middleware(self):
        """Configure all middleware."""
        # Add CORS middleware with comprehensive origins
        allowed_origins = [
            "http://localhost:5173",
            "http://localhost:3000", 
            "http://localhost:80",
            "http://localhost",
            "https://localhost:5173",
            "http://127.0.0.1:5173",
            "https://127.0.0.1:5173"
        ]
        
        # Add any additional origins from settings
        if hasattr(settings, 'ALLOWED_ORIGINS') and settings.ALLOWED_ORIGINS:
            if isinstance(settings.ALLOWED_ORIGINS, list):
                allowed_origins.extend(settings.ALLOWED_ORIGINS)
            elif settings.ALLOWED_ORIGINS != "*":
                allowed_origins.append(settings.ALLOWED_ORIGINS)
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
            allow_headers=["*"],
            expose_headers=["*"],
            max_age=600
        )
        logger.info(f"Configured CORS with allowed origins: {allowed_origins}")
        
        # Add custom middleware
        self.app.middleware("http")(add_process_time_header)
        self.app.middleware("http")(add_security_headers)
        self.app.middleware("http")(rate_limit_middleware)
        
        # Add trusted host middleware for production
        if settings.ENVIRONMENT == "production":
            self.app.add_middleware(
                TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS
            )
            logger.info(f"Added TrustedHostMiddleware with hosts: {settings.ALLOWED_HOSTS}")
    
    def _configure_routers(self):
        """Configure all API routers."""
        self.app.include_router(general.router)
        self.app.include_router(chat.router)
        self.app.include_router(documents.router)
        self.app.include_router(proxy.router)
        self.app.include_router(vector_management.router)
        self.app.include_router(rag_router, prefix="/api/rag")
        self.app.include_router(title_router)
        self.app.include_router(api_keys_router)
        logger.info("API routers configured")
    
    def _configure_exception_handlers(self):
        """Configure global exception handlers."""
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail}
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {str(exc)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
        
        logger.info("Exception handlers configured")
    
    def get_app(self) -> FastAPI:
        """Get the configured FastAPI application instance."""
        return self.app

# Application factory function
def create_application() -> FastAPI:
    """Create and return a configured FastAPI application."""
    return Application().get_app()