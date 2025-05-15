import os
import secrets
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings using Pydantic for validation and environment loading."""
    
    # API Settings
    API_TITLE: str = "Afeka ChatBot API"
    API_DESCRIPTION: str = "Backend API for Afeka College Regulations ChatBot"
    API_VERSION: str = "1.0.0"
    DOCS_URL: str = "/api/docs"
    REDOC_URL: str = "/api/redoc"
    OPENAPI_URL: str = "/api/openapi.json"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: os.environ.get(
            "ALLOWED_ORIGINS", 
            "http://localhost:5173,http://localhost:80,http://localhost"
        ).split(",")
    )
    
    # Trusted Hosts for Production
    ALLOWED_HOSTS: List[str] = Field(
        default_factory=lambda: os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
    )
    
    # Environment Setting
    ENVIRONMENT: str = Field(default=os.environ.get("ENV", "development"))
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(default=os.environ.get("SUPABASE_URL", ""))
    SUPABASE_KEY: str = Field(default=os.environ.get("SUPABASE_KEY", ""))
    
    # AI Service Configuration
    AI_SERVICE_URL: str = Field(default=os.environ.get("AI_SERVICE_URL", "http://localhost:5000"))
    
    # Security Configuration
    API_KEY_NAME: str = "X-API-Key"
    INTERNAL_API_KEY: str = Field(default=os.environ.get("INTERNAL_API_KEY", secrets.token_urlsafe(32)))
    
    # Rate Limiting
    API_RATE_LIMIT: int = Field(default=int(os.environ.get("API_RATE_LIMIT", "100")))
    
    # Document Size Limit
    MAX_DOCUMENT_SIZE_KB: int = Field(default=int(os.environ.get("MAX_DOCUMENT_SIZE_KB", "100")))
    
    @property
    def MAX_DOCUMENT_SIZE_BYTES(self) -> int:
        return self.MAX_DOCUMENT_SIZE_KB * 1024
    
    # Chat Message Length
    MAX_CHAT_MESSAGE_LENGTH: int = Field(default=int(os.environ.get("MAX_CHAT_MESSAGE_LENGTH", "1000")))

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

# Create singleton instance
settings = Settings()