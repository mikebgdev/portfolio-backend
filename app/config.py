import secrets
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str
    postgres_db: str = "portfolio_db"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Authentication (only for SQLAdmin)
    secret_key: str

    # Application Settings
    debug: bool = False

    # Multilingual Settings
    supported_languages: dict = {"en": "English", "es": "Español"}
    default_language: str = "en"

    # Security Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_per_minute: int = 100
    enable_rate_limiting: bool = True

    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True

    @property
    def effective_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.is_production:
            # In production, never allow wildcard origins
            if "*" in self.cors_origins:
                raise ValueError("Wildcard CORS origins not allowed in production")
            return self.cors_origins
        else:
            # In development, allow configured origins or wildcard for testing
            return self.cors_origins if self.cors_origins else ["*"]

    # Environment
    environment: str = "development"  # development, production

    # Cache Settings (memory-based)
    cache_ttl_default: int = 300  # Default cache TTL in seconds (5 minutes)
    cache_ttl_content: int = 600  # Content cache TTL (10 minutes)
    cache_ttl_static: int = 3600  # Static content cache TTL (1 hour)
    enable_http_cache: bool = True
    enable_compression: bool = True

    # File Storage Settings
    uploads_path: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_extensions: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    allowed_file_extensions: List[str] = [".pdf", ".doc", ".docx", ".txt"]

    # Security Settings
    admin_session_expire_hours: int = 24
    max_login_attempts: int = 5
    login_attempt_window_minutes: int = 15

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    @property
    def should_enable_cache(self) -> bool:
        """Enable cache only in production"""
        return self.is_production and self.enable_http_cache

    class Config:
        env_file = ".env"


settings = Settings()
