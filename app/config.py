from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database Configuration
    database_url: str
    postgres_user: str = "portfolio_user"
    postgres_password: str = "password"
    postgres_db: str = "portfolio_db"
    
    # Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    
    # Application Settings
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()