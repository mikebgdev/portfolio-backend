from pydantic_settings import BaseSettings
from typing import List


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
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    
    # Application Settings
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()