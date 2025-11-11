"""
Dependency Injection
Shared dependencies for FastAPI routes
"""

from fastapi import Depends, HTTPException, Header
from typing import Optional
from app.core.config import settings
from app.services.humanizer_service import HumanizerService
from app.services.cache_service import CacheService

# Global service instances (initialized on startup)
humanizer_service: Optional[HumanizerService] = None
cache_service: Optional[CacheService] = None


def get_humanizer_service() -> HumanizerService:
    """Dependency to get humanizer service"""
    if humanizer_service is None:
        raise HTTPException(status_code=503, detail="Humanizer service not initialized")
    return humanizer_service


def get_cache_service() -> Optional[CacheService]:
    """Dependency to get cache service"""
    return cache_service


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Optional API key verification"""
    if settings.API_KEY is None:
        return True  # No API key required
    
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True


