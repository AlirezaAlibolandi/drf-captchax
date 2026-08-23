"""Storage backend interface for DRF-CaptchaX."""

from abc import ABC, abstractmethod
from typing import Optional


class CaptchaBackend(ABC):
    """Define the storage operations required by CAPTCHA validation."""

    @abstractmethod
    def store_captcha(self, captcha_id: str, text: str, timeout: int) -> None:
        """Store CAPTCHA text with an expiration timeout."""
        raise NotImplementedError

    @abstractmethod
    def get_captcha(self, captcha_id: str) -> Optional[str]:
        """Return stored CAPTCHA text or None when unavailable."""
        raise NotImplementedError

    @abstractmethod
    def delete_captcha(self, captcha_id: str) -> None:
        """Delete all state associated with a CAPTCHA identifier."""
        raise NotImplementedError

    @abstractmethod
    def get_attempts(self, captcha_id: str) -> int:
        """Return the current validation attempt count."""
        raise NotImplementedError

    @abstractmethod
    def increment_attempts(self, captcha_id: str) -> int:
        """Increment and return the validation attempt count."""
        raise NotImplementedError

    def consume_captcha(self, captcha_id: str) -> Optional[str]:
        """Return and delete a CAPTCHA, with built-in backends overriding atomically."""
        text = self.get_captcha(captcha_id)
        if text is not None:
            self.delete_captcha(captcha_id)
        return text
