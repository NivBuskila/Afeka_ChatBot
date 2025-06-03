# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env file from multiple locations
env_locations = [
    Path('.env'),  # Current directory
    Path('../.env'),  # Parent directory
    Path('../../.env'),  # Two levels up
]

for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    app_name: str = "Afeka ChatBot API"
    app_version: str = "1.0.0"
    app_description: str = "Backend API for Afeka College Regulations ChatBot"
    environment: str = Field(default="development", env="ENV")
    
    # API Configuration
    api_prefix: str = "/api"
    api_docs_url: str = "/api/docs"
    api_redoc_url: str = "/api/redoc"
    api_openapi_url: str = "/api/openapi.json"
    
    # Server
    port: int = Field(default=8000, env="PORT")
    host: str = "0.0.0.0"
    reload: bool = True
    
    # CORS - Handle both string and list formats
    allowed_origins: str | List[str] = Field(
        default="http://localhost:5173,http://localhost:80,http://localhost,http://frontend:3000,http://frontend,http://192.168.56.1:5173,http://172.16.16.179:5173,http://172.20.224.1:5173",
        env="ALLOWED_ORIGINS"
    )
    
    # Security
    internal_api_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="INTERNAL_API_KEY"
    )
    
    api_key_header_name: str = "X-API-Key"


    # Rate Limiting
    api_rate_limit: int = Field(default=100, env="API_RATE_LIMIT")
    
    # Database - Support multiple possible environment variable names
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    supabase_service_key: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_KEY")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    
    # AI Service
    ai_service_url: str = Field(
        default="http://localhost:5000",
        env="AI_SERVICE_URL"
    )
    
    # Trusted Hosts (for production)
    allowed_hosts: str | List[str] = Field(
        default="localhost",
        env="ALLOWED_HOSTS"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list"""
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list"""
        if isinstance(self.allowed_hosts, str):
            return [host.strip() for host in self.allowed_hosts.split(",")]
        return self.allowed_hosts
    
    @property
    def get_supabase_key_value(self) -> Optional[str]:
        """Get the actual Supabase key, trying all possible options"""
        return self.supabase_key or self.supabase_service_key or self.supabase_anon_key
        

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        # Allow extra fields for forward compatibility
        extra = "allow"
        
        # Pydantic v2 config
        env_file_encoding = 'utf-8'


# Create a singleton instance
settings = Settings()

# Debug logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Loaded settings - Supabase URL: {settings.supabase_url is not None}")
logger.info(f"Loaded settings - Supabase key available: {settings.get_supabase_key_value is not None}")
