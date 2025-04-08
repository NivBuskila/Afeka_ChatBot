import os
import sys
import logging
import uvicorn

# הוספת תיקיית השורש לנתיב החיפוש של Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, project_root)

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
# Remove direct load_dotenv, config will handle it
# from dotenv import load_dotenv 

# ייבוא רגיל
try:
    # Import config using absolute imports
    from backend.core import config

    # Import middleware with absolute imports
    from backend.middleware.timing import add_process_time_header
    from backend.middleware.security import add_security_headers
    from backend.middleware.rate_limit import rate_limit_middleware

    # Import routers with absolute imports
    from backend.api.routers import general, chat, documents
except ImportError:
    # ניסיון ייבוא מקומי אם הייבוא הרגיל נכשל
    # Import config using relative imports
    from src.backend.core import config

    # Import middleware with relative imports
    from src.backend.middleware.timing import add_process_time_header
    from src.backend.middleware.security import add_security_headers
    from src.backend.middleware.rate_limit import rate_limit_middleware

    # Import routers with relative imports
    from src.backend.api.routers import general, chat, documents

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables - Handled in config.py
# load_dotenv()

# Initialize FastAPI app using config
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    openapi_url=config.OPENAPI_URL
)

# Define allowed origins for CORS using config
logger.info(f"Configured CORS with allowed origins: {config.ALLOWED_ORIGINS}")

# Add CORS middleware using config
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", config.API_KEY_NAME], # Use config for API key name
    max_age=600
)

# Add custom middleware
app.middleware("http")(add_process_time_header)
app.middleware("http")(add_security_headers)
app.middleware("http")(rate_limit_middleware)

# Add trusted host middleware for production using config
if config.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=config.ALLOWED_HOSTS
    )
    logger.info(f"Added TrustedHostMiddleware with hosts: {config.ALLOWED_HOSTS}")

# Include routers
app.include_router(general.router)
app.include_router(chat.router)
app.include_router(documents.router)

# Error handlers (keep these global handlers)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    # Consider adding more details in development mode
    # import traceback
    # logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"} # Avoid leaking exception details
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    # Use reload=True only for development using config
    reload_flag = config.ENVIRONMENT == "development"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload_flag) 