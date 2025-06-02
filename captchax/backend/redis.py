"""
Redis-based storage backend for CAPTCHA data.

This module provides a Redis-based implementation for storing
CAPTCHA validation data, suitable for production use.
"""

from typing import Optional
import redis
from . import CaptchaBackend
from ..settings import CAPTCHAX_CONFIG, get_redis_client


class RedisBackend(CaptchaBackend):
    """
    Redis storage backend for CAPTCHA data.
    
    This backend uses Redis for storing CAPTCHA data, providing
    persistence and scalability suitable for production use.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the Redis backend.
        
        Args:
            redis_client: Optional Redis client instance
        """
        self.redis = redis_client or get_redis_client()
        if not self.redis:
            raise ValueError("Redis client is required")
            
        self.prefix = CAPTCHAX_CONFIG["REDIS_PREFIX"]
        
    def _get_captcha_key(self, captcha_id: str) -> str:
        """Get Redis key for CAPTCHA data."""
        return f"{self.prefix}captcha:{captcha_id}"
        
    def _get_attempts_key(self, captcha_id: str) -> str:
        """Get Redis key for attempts counter."""
        return f"{self.prefix}attempts:{captcha_id}"
        
    def store_captcha(self, captcha_id: str, text: str, timeout: int) -> None:
        """Store CAPTCHA text with expiration."""
        captcha_key = self._get_captcha_key(captcha_id)
        attempts_key = self._get_attempts_key(captcha_id)
        
        pipe = self.redis.pipeline()
        pipe.setex(captcha_key, timeout, text)
        pipe.setex(attempts_key, timeout, 0)
        pipe.execute()
        
    def get_captcha(self, captcha_id: str) -> Optional[str]:
        """Get stored CAPTCHA text."""
        value = self.redis.get(self._get_captcha_key(captcha_id))
        return value.decode() if value else None
        
    def delete_captcha(self, captcha_id: str) -> None:
        """Delete stored CAPTCHA data."""
        pipe = self.redis.pipeline()
        pipe.delete(self._get_captcha_key(captcha_id))
        pipe.delete(self._get_attempts_key(captcha_id))
        pipe.execute()
        
    def get_attempts(self, captcha_id: str) -> int:
        """Get number of validation attempts."""
        value = self.redis.get(self._get_attempts_key(captcha_id))
        return int(value) if value else 0
        
    def increment_attempts(self, captcha_id: str) -> int:
        """Increment validation attempts counter."""
        key = self._get_attempts_key(captcha_id)
        value = self.redis.incr(key)
        return int(value) if value else 0