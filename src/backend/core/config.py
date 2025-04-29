import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Settings
API_TITLE = "Afeka ChatBot API"
API_DESCRIPTION = "Backend API for Afeka ChatBot"
API_VERSION = "1.0.0"
DOCS_URL = "/docs"
REDOC_URL = "/redoc"
OPENAPI_URL = "/openapi.json"

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# API Key
API_KEY_NAME = "X-API-Key"

# CORS Settings
ALLOWED_ORIGINS = ["*"]

# Security Settings
ALLOWED_HOSTS = ["*"]

# AI Service Settings
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:5000")

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wzvyibgtfwvmbfaybmqx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Rate Limiting
API_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT", "100"))

# Other settings
# Example: Max document size
MAX_DOCUMENT_SIZE_KB = int(os.environ.get("MAX_DOCUMENT_SIZE_KB", "100"))
MAX_DOCUMENT_SIZE_BYTES = MAX_DOCUMENT_SIZE_KB * 1024

MAX_CHAT_MESSAGE_LENGTH = int(os.environ.get("MAX_CHAT_MESSAGE_LENGTH", "1000")) 