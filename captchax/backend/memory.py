"""
Memory-based storage backend for CAPTCHA data.

This module provides a simple in-memory storage implementation
for CAPTCHA validation data, suitable for development and testing.
"""

import time
from typing import Dict, Optional, Tuple
from . import CaptchaBackend


class MemoryBackend(CaptchaBackend):
    """
    In-memory storage backend for CAPTCHA data.
    
    This backend stores CAPTCHA data in memory using dictionaries.
    It's suitable for development and testing but not recommended
    for production use due to lack of persistence and scalability.
    """
    
    def __init__(self):
        """Initialize the memory storage."""
        self._storage: Dict[str, Tuple[str, int, int]] = {}  # id -> (text, expiry, attempts)
        
    def _cleanup_expired(self) -> None:
        """Remove expired CAPTCHA entries."""
        current_time = int(time.time())
        expired = [k for k, v in self._storage.items() if v[1] < current_time]
        for key in expired:
            del self._storage[key]
            
    def store_captcha(self, captcha_id: str, text: str, timeout: int) -> None:
        """Store a CAPTCHA text with expiration."""
        expiry = int(time.time()) + timeout
        self._storage[captcha_id] = (text, expiry, 0)
        self._cleanup_expired()
        
    def get_captcha(self, captcha_id: str) -> Optional[str]:
        """Get stored CAPTCHA text if not expired."""
        self._cleanup_expired()
        if captcha_id in self._storage:
            return self._storage[captcha_id][0]
        return None
        
    def delete_captcha(self, captcha_id: str) -> None:
        """Delete a stored CAPTCHA."""
        if captcha_id in self._storage:
            del self._storage[captcha_id]
            
    def get_attempts(self, captcha_id: str) -> int:
        """Get number of validation attempts."""
        self._cleanup_expired()
        if captcha_id in self._storage:
            return self._storage[captcha_id][2]
        return 0
        
    def increment_attempts(self, captcha_id: str) -> int:
        """Increment validation attempts counter."""
        self._cleanup_expired()
        if captcha_id in self._storage:
            text, expiry, attempts = self._storage[captcha_id]
            attempts += 1
            self._storage[captcha_id] = (text, expiry, attempts)
            return attempts
        return 0