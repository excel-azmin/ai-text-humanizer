"""
Health Check Endpoints
"""

from fastapi import APIRouter, Depends
import torch
from app.models.schemas import HealthResponse
from app.core.dependencies import get_humanizer_service, get_cache_service
from app.core.config import settings
from app.services.humanizer_service import HumanizerService
from app.services.cache_service import CacheService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check(
    humanizer_service: HumanizerService = Depends(get_humanizer_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        models_loaded=humanizer_service.is_initialized(),
        cache_available=cache_service.is_available() if cache_service else False,
        gpu_available=torch.cuda.is_available(),
        version=settings.APP_VERSION
    )


