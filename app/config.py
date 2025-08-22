from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_db: str = "portfolio_db"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Authentication (only for SQLAdmin)
    secret_key: str = ""

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
    cors_origins_raw: Union[str, List[str]] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ],
        alias="CORS_ORIGINS",
        description="Allowed CORS origins (comma-separated in env: CORS_ORIGINS)",
    )
    cors_allow_credentials: bool = True
    cors_allow_all_origins: bool = (
        False  # Set to True to allow all origins in development
    )

    @field_validator("cors_origins_raw", mode="before")
    @classmethod
    def parse_cors_origins_raw(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            # Handle empty strings
            if not v.strip():
                return []
            # If it's a string, split by comma and strip whitespace
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else []
        elif v is None:
            return []
        return v

    @property
    def cors_origins(self) -> List[str]:
        """Get parsed CORS origins."""
        if isinstance(self.cors_origins_raw, list):
            return self.cors_origins_raw
        return []

    @property
    def effective_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.is_production:
            # In production, never allow wildcard origins
            if "*" in self.cors_origins or self.cors_allow_all_origins:
                raise ValueError("Wildcard CORS origins not allowed in production")
            return self.cors_origins
        else:
            # Check if wildcard is explicitly allowed
            if self.cors_allow_all_origins:
                return ["*"]

            # In development, be more permissive and include common development ports
            dev_origins = self.cors_origins.copy()

            # Add common development origins if not already present
            common_dev_origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8080",
                "http://127.0.0.1:8080",
                "http://localhost:5173",
                "http://127.0.0.1:5173",  # Vite
                "http://localhost:4200",
                "http://127.0.0.1:4200",  # Angular
                "http://localhost:8000",
                "http://127.0.0.1:8000",  # Alternative dev server
                "http://localhost:3001",
                "http://127.0.0.1:3001",  # Alternative React port
            ]

            for origin in common_dev_origins:
                if origin not in dev_origins:
                    dev_origins.append(origin)

            return dev_origins

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
