"""
CAPTCHA storage backend package.

This package provides storage backends for CAPTCHA data,
including memory-based and Redis-based implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional


class CaptchaBackend(ABC):
    """
    Abstract base class for CAPTCHA storage backends.
    """
    
    @abstractmethod
    def store_captcha(self, captcha_id: str, text: str, timeout: int) -> None:
        """
        Store a CAPTCHA text with its ID.
        
        Args:
            captcha_id: Unique identifier for the CAPTCHA
            text: The CAPTCHA text to store
            timeout: Time in seconds until the CAPTCHA expires
        """
        pass
        
    @abstractmethod
    def get_captcha(self, captcha_id: str) -> Optional[str]:
        """
        Retrieve a stored CAPTCHA text.
        
        Args:
            captcha_id: The CAPTCHA ID to look up
            
        Returns:
            The stored CAPTCHA text or None if not found
        """
        pass
        
    @abstractmethod
    def delete_captcha(self, captcha_id: str) -> None:
        """
        Delete a stored CAPTCHA.
        
        Args:
            captcha_id: The CAPTCHA ID to delete
        """
        pass
        
    @abstractmethod
    def get_attempts(self, captcha_id: str) -> int:
        """
        Get the number of validation attempts for a CAPTCHA.
        
        Args:
            captcha_id: The CAPTCHA ID to check
            
        Returns:
            Number of validation attempts
        """
        pass
        
    @abstractmethod
    def increment_attempts(self, captcha_id: str) -> int:
        """
        Increment the number of validation attempts.
        
        Args:
            captcha_id: The CAPTCHA ID to increment
            
        Returns:
            New number of attempts
        """
        pass