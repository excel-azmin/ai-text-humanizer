"""
Cache Service
Redis-based caching for humanization results
"""

import json
import hashlib
from typing import Optional, Dict
import redis
from app.core.config import settings
from app.core.logging import logger


class CacheService:
    """Redis cache service for humanization results"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.enabled = False
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        if not settings.CACHE_ENABLED:
            logger.info("Caching disabled in configuration")
            return
        
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            self.enabled = True
            logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Caching disabled.")
            self.enabled = False
            self.client = None
    
    def generate_key(self, text: str, mode: str, intensity: float) -> str:
        """Generate cache key from parameters"""
        content = f"{text}:{mode}:{intensity}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Dict]:
        """Get cached result"""
        if not self.enabled or not self.client:
            return None
        
        try:
            cached = self.client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    async def set(self, key: str, value: Dict, ttl: Optional[int] = None) -> bool:
        """Cache result with TTL"""
        if not self.enabled or not self.client:
            return False
        
        try:
            ttl = ttl or settings.CACHE_TTL
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if cache is available"""
        return self.enabled and self.client is not None


