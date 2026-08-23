"""Redis-backed CAPTCHA storage backend."""

from typing import Any, Optional

from . import CaptchaBackend
from ..settings import get_config, get_redis_client


class RedisBackend(CaptchaBackend):
    """Store CAPTCHA state in Redis for multi-process deployments."""

    def __init__(self, redis_client: Optional[Any] = None, prefix: Optional[str] = None):
        """Initialize the backend with an injected or configured Redis client."""
        self.redis = redis_client if redis_client is not None else get_redis_client()
        if self.redis is None:
            raise ValueError("Redis client is required")
        self.prefix = prefix if prefix is not None else get_config()["REDIS_PREFIX"]

    def _get_captcha_key(self, captcha_id: str) -> str:
        """Return the Redis key used for CAPTCHA text."""
        return f"{self.prefix}captcha:{captcha_id}"

    def _get_attempts_key(self, captcha_id: str) -> str:
        """Return the Redis key used for validation attempts."""
        return f"{self.prefix}attempts:{captcha_id}"

    def store_captcha(self, captcha_id: str, text: str, timeout: int) -> None:
        """Store CAPTCHA text and attempt state with the same TTL."""
        captcha_key = self._get_captcha_key(captcha_id)
        attempts_key = self._get_attempts_key(captcha_id)
        pipe = self.redis.pipeline()
        pipe.setex(captcha_key, timeout, text)
        pipe.setex(attempts_key, timeout, 0)
        pipe.execute()

    def get_captcha(self, captcha_id: str) -> Optional[str]:
        """Return stored CAPTCHA text."""
        value = self.redis.get(self._get_captcha_key(captcha_id))
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else str(value)

    def delete_captcha(self, captcha_id: str) -> None:
        """Delete CAPTCHA text and attempt state in one Redis transaction."""
        pipe = self.redis.pipeline()
        pipe.delete(self._get_captcha_key(captcha_id))
        pipe.delete(self._get_attempts_key(captcha_id))
        pipe.execute()

    def consume_captcha(self, captcha_id: str) -> Optional[str]:
        """Atomically return and delete CAPTCHA text plus attempt state."""
        script = (
            "local value = redis.call('GET', KEYS[1]); "
            "if value then redis.call('DEL', KEYS[1], KEYS[2]); end; "
            "return value"
        )
        value = self.redis.eval(
            script,
            2,
            self._get_captcha_key(captcha_id),
            self._get_attempts_key(captcha_id),
        )
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else str(value)

    def get_attempts(self, captcha_id: str) -> int:
        """Return the current validation attempt count."""
        value = self.redis.get(self._get_attempts_key(captcha_id))
        return int(value) if value is not None else 0

    def increment_attempts(self, captcha_id: str) -> int:
        """Increment attempts while keeping its TTL aligned with the CAPTCHA key."""
        attempts_key = self._get_attempts_key(captcha_id)
        captcha_key = self._get_captcha_key(captcha_id)
        pipe = self.redis.pipeline()
        pipe.incr(attempts_key)
        pipe.ttl(captcha_key)
        attempts, ttl = pipe.execute()

        if ttl == -2:
            self.redis.delete(attempts_key)
            return 0
        if ttl >= 0:
            self.redis.expire(attempts_key, max(int(ttl), 1))
        return int(attempts)
