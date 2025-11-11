"""
API v1 Router
Combines all v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1 import health, humanize, analyze, techniques

api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(health.router)
api_router.include_router(humanize.router)
api_router.include_router(analyze.router)
api_router.include_router(techniques.router)


