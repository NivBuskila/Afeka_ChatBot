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
from ..api import vector_management

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
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", settings.API_KEY_NAME],
            max_age=600
        )
        logger.info(f"Configured CORS with allowed origins: {settings.ALLOWED_ORIGINS}")
        
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