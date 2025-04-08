import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_TITLE = "APEX API"
API_DESCRIPTION = "API for Afeka's Professional Engineering Experience"
API_VERSION = "0.1.0"

# Security Settings
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
API_KEY_NAME = os.environ.get("API_KEY_NAME", "X-API-Key")

# Documentation URLs
DOCS_URL = "/docs" if ENVIRONMENT != "production" else None
REDOC_URL = "/redoc" if ENVIRONMENT != "production" else None
OPENAPI_URL = "/openapi.json" if ENVIRONMENT != "production" else None

# Rate Limiting
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "100"))  # requests per minute
RATE_LIMIT_EXPIRY = int(os.environ.get("RATE_LIMIT_EXPIRY", "3600"))  # seconds

# CORS Settings
ALLOWED_ORIGINS = [
    # Frontend URLs (local and production)
    "http://localhost:5173",  # Local frontend dev
    "http://localhost:80",    # Local production
    "http://localhost",       # Local alternate
    "http://frontend:3000",   # Docker service
    "http://frontend:80",     # Docker service prod
    "https://example.com",    # Production URL (update when deployed)
    
    # Development and testing
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:80",
    "http://127.0.0.1",
    "*",  # Allow all during development (REMOVE IN PRODUCTION)
]

# Trusted Host Settings
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "backend",  # Docker service name
    "example.com",  # Production domain (update when deployed)
]

# Service Connection
AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:5000")

# Application Settings
MAX_CHAT_MESSAGE_LENGTH = int(os.environ.get("MAX_CHAT_MESSAGE_LENGTH", "2000"))
MAX_DOCUMENT_SIZE = int(os.environ.get("MAX_DOCUMENT_SIZE", "10485760"))  # 10 MB

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wzvyibgtfwvmbfaybmqx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# הוספת קונפיגורציה ל-Gemini API ישירות בבקאנד למקרה שנרצה לגשת ישירות
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyB0D4QL-SIoR8LR4WkVRjxUV_HyIUQBdCU')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-pro')
GEMINI_TEMPERATURE = float(os.environ.get('GEMINI_TEMPERATURE', '0.7'))
GEMINI_MAX_OUTPUT_TOKENS = int(os.environ.get('GEMINI_MAX_OUTPUT_TOKENS', '1024'))

# Security Configuration
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", secrets.token_urlsafe(32))

# Other settings
# Example: Max document size
MAX_DOCUMENT_SIZE_KB = int(os.environ.get("MAX_DOCUMENT_SIZE_KB", "100"))
MAX_DOCUMENT_SIZE_BYTES = MAX_DOCUMENT_SIZE_KB * 1024 