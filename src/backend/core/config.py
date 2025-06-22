import os
import secrets
from dotenv import load_dotenv

load_dotenv()

API_TITLE = "Afeka ChatBot API"
API_DESCRIPTION = "Backend API for Afeka College Regulations ChatBot"
API_VERSION = "1.0.0"
DOCS_URL = "/api/docs"
REDOC_URL = "/api/redoc"
OPENAPI_URL = "/api/openapi.json"

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:80,http://localhost,http://frontend:3000,http://frontend"
).split(",")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

ENVIRONMENT = os.environ.get("ENV", "development")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wzvyibgtfwvmbfaybmqx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:5000")

API_KEY_NAME = "X-API-Key"
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", secrets.token_urlsafe(32))

API_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT", "500"))

MAX_DOCUMENT_SIZE_KB = int(os.environ.get("MAX_DOCUMENT_SIZE_KB", "100"))
MAX_DOCUMENT_SIZE_BYTES = MAX_DOCUMENT_SIZE_KB * 1024

MAX_CHAT_MESSAGE_LENGTH = int(os.environ.get("MAX_CHAT_MESSAGE_LENGTH", "1000"))