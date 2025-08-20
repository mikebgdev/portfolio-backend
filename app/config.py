from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database Configuration
    postgres_host: str = "192.168.10.200"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "changeme"
    postgres_db: str = "portfolio_db"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth (optional for CI/testing)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    # Application Settings
    debug: bool = False
    # Always allow all origins for development - more permissive approach
    cors_origins: List[str] = ["*"]
    
    @property
    def get_cors_origins(self) -> List[str]:
        # Always return permissive CORS for development
        return ["*"]
    
    # Multilingual Settings
    supported_languages: dict = {
        'en': 'English',
        'es': 'Español'
    }
    default_language: str = 'en'
    
    # Security Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_per_minute: int = 100
    enable_rate_limiting: bool = True
    
    # Cache Settings
    redis_url: Optional[str] = None  # Redis connection URL (optional)
    cache_ttl_default: int = 300  # Default cache TTL in seconds (5 minutes)
    cache_ttl_content: int = 600  # Content cache TTL (10 minutes)
    cache_ttl_static: int = 3600  # Static content cache TTL (1 hour)
    enable_http_cache: bool = True
    enable_compression: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()