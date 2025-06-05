# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# ✅ STANDARDIZED: Load .env from project root
project_root = Path(__file__).parent.parent.parent.parent  # Go up to project root
env_file = project_root / ".env"

if env_file.exists():
    load_dotenv(env_file, override=True)
    print(f"✅ Loaded environment from: {env_file}")
else:
    print(f"⚠️  Environment file not found: {env_file}")

class AIServiceConfig:
    """AI Service configuration settings"""
    
    def __init__(self, settings_instance):
        self.base_url: str = settings_instance.ai_service_url
        self.timeout: int = settings_instance.ai_service_timeout
        self.max_retries: int = settings_instance.ai_service_max_retries
        self.retry_delay: float = settings_instance.ai_service_retry_delay
        self.connection_timeout: int = settings_instance.ai_service_connection_timeout
        self.read_timeout: int = settings_instance.ai_service_read_timeout
        self.enable_health_check: bool = settings_instance.ai_service_enable_health_check
        self.health_check_interval: int = settings_instance.ai_service_health_check_interval
        
    @property
    def chat_endpoint(self) -> str:
        return f"{self.base_url}/chat"
    
    @property
    def search_endpoint(self) -> str:
        return f"{self.base_url}/rag/search"
    
    @property
    def hybrid_search_endpoint(self) -> str:
        return f"{self.base_url}/rag/search/hybrid"
    
    @property
    def enhanced_search_endpoint(self) -> str:
        return f"{self.base_url}/rag/enhanced_search"
    
    @property
    def stats_endpoint(self) -> str:
        return f"{self.base_url}/rag/stats"
    
    @property
    def health_endpoint(self) -> str:
        return f"{self.base_url}/"
    
    def document_reprocess_endpoint(self, document_id: int) -> str:
        return f"{self.base_url}/rag/document/{document_id}/reprocess"


class Settings(BaseSettings):
    """Application settings with validation and standardized environment variables"""
    
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
    host: str = Field(default="0.0.0.0", env="HOST")
    reload: bool = Field(default=True, env="RELOAD")
    
    # CORS
    allowed_origins: str | List[str] = Field(
        default="http://localhost:5173,http://localhost:80,http://localhost",
        env="ALLOWED_ORIGINS"
    )
    
    # Security
    internal_api_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="INTERNAL_API_KEY"
    )
    
    # Rate Limiting
    api_rate_limit: int = Field(default=100, env="API_RATE_LIMIT")
    
    # ✅ STANDARDIZED: Unified Supabase Configuration
    supabase_url: str = Field(env="SUPABASE_URL")
    supabase_key: str = Field(env="SUPABASE_KEY")  # Main key for backend
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    supabase_service_key: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_KEY")
    
    # ✅ STANDARDIZED: AI Service Configuration
    ai_service_url: str = Field(default="http://localhost:5000", env="AI_SERVICE_URL")
    ai_service_timeout: int = Field(default=30, env="AI_SERVICE_TIMEOUT")
    ai_service_connection_timeout: int = Field(default=5, env="AI_SERVICE_CONNECTION_TIMEOUT")
    ai_service_read_timeout: int = Field(default=25, env="AI_SERVICE_READ_TIMEOUT")
    ai_service_max_retries: int = Field(default=3, env="AI_SERVICE_MAX_RETRIES")
    ai_service_retry_delay: float = Field(default=1.0, env="AI_SERVICE_RETRY_DELAY")
    ai_service_enable_health_check: bool = Field(default=True, env="AI_SERVICE_ENABLE_HEALTH_CHECK")
    ai_service_health_check_interval: int = Field(default=60, env="AI_SERVICE_HEALTH_CHECK_INTERVAL")
    
    # Trusted Hosts
    allowed_hosts: str | List[str] = Field(default="localhost", env="ALLOWED_HOSTS")
    
    # ✅ SIMPLE: Basic Context Configuration
    chat_context_window_size: int = Field(default=10, env="CHAT_CONTEXT_WINDOW_SIZE")
    chat_max_context_tokens: int = Field(default=4000, env="CHAT_MAX_CONTEXT_TOKENS")
    chat_context_enabled: bool = Field(default=True, env="CHAT_CONTEXT_ENABLED")
    
    # ✅ NEW: Advanced Context Settings
    chat_context_relevance_threshold: float = Field(default=0.1, env="CHAT_CONTEXT_RELEVANCE_THRESHOLD")
    chat_context_max_age_hours: int = Field(default=24, env="CHAT_CONTEXT_MAX_AGE_HOURS")
    chat_context_cache_ttl_minutes: int = Field(default=30, env="CHAT_CONTEXT_CACHE_TTL_MINUTES")
    
    # ✅ NEW: Validation without defaults
    @validator('supabase_url')
    def validate_supabase_url(cls, v):
        if not v:
            raise ValueError('SUPABASE_URL is required')
        return v
    
    @validator('supabase_key')
    def validate_supabase_key(cls, v):
        if not v:
            raise ValueError('SUPABASE_KEY is required')
        return v
    
    @property
    def allowed_origins_list(self) -> List[str]:
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(',')]
        return self.allowed_origins
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        if isinstance(self.allowed_hosts, str):
            return [host.strip() for host in self.allowed_hosts.split(',')]
        return self.allowed_hosts
    
    @property
    def get_supabase_key_value(self) -> str:
        """Get the primary Supabase key for backend operations"""
        return self.supabase_service_key or self.supabase_key
    
    @property
    def ai_service_config(self) -> AIServiceConfig:
        """Get AI service configuration object"""
        return AIServiceConfig(self)
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
        env_file_encoding = 'utf-8'

# ✅ GLOBAL: Create settings instance
settings = Settings()

# ✅ VALIDATION: Print configuration status
print(f"🔧 Backend Configuration Loaded:")
print(f"   Environment: {settings.environment}")
print(f"   Supabase URL: {settings.supabase_url}")
print(f"   AI Service URL: {settings.ai_service_url}")
print(f"   Context Window Size: {settings.chat_context_window_size}")
