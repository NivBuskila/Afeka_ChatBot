import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Settings
API_TITLE = "Afeka ChatBot API"
API_DESCRIPTION = "Backend API for Afeka College Regulations ChatBot"
API_VERSION = "1.0.0"
DOCS_URL = "/api/docs"
REDOC_URL = "/api/redoc"
OPENAPI_URL = "/api/openapi.json"

# CORS Settings
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:80,http://localhost,http://frontend:3000,http://frontend"
).split(",")

# Trusted Hosts for Production
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

# Environment Setting
ENVIRONMENT = os.environ.get("ENV", "development")

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wzvyibgtfwvmbfaybmqx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# AI Service Configuration
AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:5000")

# Security Configuration
API_KEY_NAME = "X-API-Key"
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", secrets.token_urlsafe(32))

# Rate Limiting
API_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT", "100"))

# Other settings
# Example: Max document size
MAX_DOCUMENT_SIZE_KB = int(os.environ.get("MAX_DOCUMENT_SIZE_KB", "100"))
MAX_DOCUMENT_SIZE_BYTES = MAX_DOCUMENT_SIZE_KB * 1024

MAX_CHAT_MESSAGE_LENGTH = int(os.environ.get("MAX_CHAT_MESSAGE_LENGTH", "1000")) 