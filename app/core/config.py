"""
Application Configuration
Environment-based settings management
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore unknown/legacy environment variables (e.g., API_PORT, MODEL_SIZE)
    )
    
    # Application
    APP_NAME: str = "AI Text Humanizer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 3650
    WORKERS: int = 4
    RELOAD: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_ENABLED: bool = True
    
    # Model Configuration
    USE_GPU: bool = True
    MODEL_SIZE_FAST: str = "small"
    MODEL_SIZE_BALANCED: str = "medium"
    MODEL_SIZE_QUALITY: str = "large"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Security
    API_KEY: Optional[str] = None
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Paths
    STATIC_DIR: str = "static"
    TEMPLATES_DIR: str = "templates"
    MODELS_DIR: str = "models"
    CACHE_DIR: str = "cache"
    LOGS_DIR: str = "logs"


# Global settings instance
settings = Settings()

# Create necessary directories
for directory in [settings.STATIC_DIR, settings.TEMPLATES_DIR, 
                  settings.MODELS_DIR, settings.CACHE_DIR, settings.LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

