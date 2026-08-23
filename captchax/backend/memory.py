"""Thread-safe in-process CAPTCHA storage backend."""

import threading
import time
from typing import Optional

from . import CaptchaBackend


class MemoryBackend(CaptchaBackend):
    """Store CAPTCHA state in process memory shared by all backend instances."""

    _storage: dict[str, tuple[str, float, int]] = {}
    _lock = threading.RLock()

    def _cleanup_expired(self, now: Optional[float] = None) -> None:
        """Remove expired CAPTCHA entries."""
        current_time = time.monotonic() if now is None else now
        expired = [
            captcha_id
            for captcha_id, (_, expiry, _) in self._storage.items()
            if expiry <= current_time
        ]
        for captcha_id in expired:
            self._storage.pop(captcha_id, None)

    def store_captcha(self, captcha_id: str, text: str, timeout: int) -> None:
        """Store CAPTCHA text with an expiration time and reset its attempt count."""
        expiry = time.monotonic() + max(float(timeout), 0.0)
        with self._lock:
            self._cleanup_expired()
            self._storage[captcha_id] = (text, expiry, 0)

    def get_captcha(self, captcha_id: str) -> Optional[str]:
        """Return CAPTCHA text when the entry exists and has not expired."""
        with self._lock:
            self._cleanup_expired()
            value = self._storage.get(captcha_id)
            return value[0] if value else None

    def delete_captcha(self, captcha_id: str) -> None:
        """Delete CAPTCHA state if it exists."""
        with self._lock:
            self._storage.pop(captcha_id, None)

    def consume_captcha(self, captcha_id: str) -> Optional[str]:
        """Atomically return and delete unexpired CAPTCHA state."""
        with self._lock:
            self._cleanup_expired()
            value = self._storage.pop(captcha_id, None)
            return value[0] if value else None

    def get_attempts(self, captcha_id: str) -> int:
        """Return the current validation attempt count."""
        with self._lock:
            self._cleanup_expired()
            value = self._storage.get(captcha_id)
            return value[2] if value else 0

    def increment_attempts(self, captcha_id: str) -> int:
        """Atomically increment and return the validation attempt count."""
        with self._lock:
            self._cleanup_expired()
            value = self._storage.get(captcha_id)
            if not value:
                return 0
            text, expiry, attempts = value
            attempts += 1
            self._storage[captcha_id] = (text, expiry, attempts)
            return attempts

    @classmethod
    def clear(cls) -> None:
        """Clear all in-process CAPTCHA state."""
        with cls._lock:
            cls._storage.clear()
