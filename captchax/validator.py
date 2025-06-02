"""
CAPTCHA validation module for Django REST Framework.

This module provides validation functionality for CAPTCHA responses,
supporting multiple storage backends and customizable validation rules.
"""

from typing import Optional, Dict, Any
from rest_framework import serializers
from rest_framework.request import Request
from django.core.exceptions import ValidationError
from .settings import CAPTCHAX_CONFIG, get_backend_class


class CaptchaValidator:
    """
    Validator class for CAPTCHA validation in DRF serializers.
    
    Attributes:
        backend: The storage backend instance for CAPTCHA validation
        case_sensitive: Whether validation should be case-sensitive
        max_attempts: Maximum number of validation attempts allowed
    """
    
    def __init__(self, 
                 case_sensitive: Optional[bool] = None,
                 max_attempts: Optional[int] = None,
                 backend_class = None,
                 **backend_kwargs):
        """
        Initialize the CAPTCHA validator.
        
        Args:
            case_sensitive: Override default case sensitivity setting
            max_attempts: Override default maximum attempts setting
            backend_class: Custom backend class to use
            **backend_kwargs: Additional arguments passed to the backend
        """
        self.case_sensitive = case_sensitive if case_sensitive is not None else CAPTCHAX_CONFIG["CASE_SENSITIVE"]
        self.max_attempts = max_attempts if max_attempts is not None else CAPTCHAX_CONFIG["MAX_ATTEMPTS"]
        
        backend_class = backend_class or get_backend_class()
        self.backend = backend_class(**backend_kwargs)

    def __call__(self, value: str) -> None:
        """
        Validate the CAPTCHA response.
        
        Args:
            value: The CAPTCHA response text to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError("CAPTCHA response must be a string")
            
        if not value.strip():
            raise ValidationError("CAPTCHA response cannot be empty")
            
        self.validate(value)

    def validate(self, captcha_text: str, captcha_id: Optional[str] = None, request: Optional[Request] = None) -> bool:
        """
        Validate a CAPTCHA response.
        
        Args:
            captcha_text: The CAPTCHA text to validate
            captcha_id: The CAPTCHA ID (optional if in request data)
            request: The request object (optional)
            
        Returns:
            bool: True if validation succeeds
            
        Raises:
            ValidationError: If validation fails
        """
        # Get captcha_id from request if not provided
        if not captcha_id and request and hasattr(request, 'data'):
            captcha_id = request.data.get("captcha_id")
            
        if not captcha_id:
            raise ValidationError("CAPTCHA ID is required")
            
        # Check attempts
        attempts = self.backend.get_attempts(captcha_id)
        if attempts >= self.max_attempts:
            self.backend.delete_captcha(captcha_id)
            raise ValidationError("Maximum CAPTCHA attempts exceeded")
            
        # Get stored CAPTCHA
        stored_text = self.backend.get_captcha(captcha_id)
        if not stored_text:
            raise ValidationError("CAPTCHA has expired or is invalid")
            
        # Validate response
        if self.case_sensitive:
            valid = stored_text == captcha_text
        else:
            valid = stored_text.upper() == captcha_text.upper()
            
        # Handle result
        if valid:
            self.backend.delete_captcha(captcha_id)
            return True
        else:
            attempts = self.backend.increment_attempts(captcha_id)
            if attempts >= self.max_attempts:
                self.backend.delete_captcha(captcha_id)
                raise ValidationError("Maximum CAPTCHA attempts exceeded")
            raise ValidationError("Invalid CAPTCHA response")

    def get_validation_data(self) -> Dict[str, Any]:
        """
        Get validation configuration data.
        
        Returns:
            Dict containing validation settings
        """
        return {
            "case_sensitive": self.case_sensitive,
            "max_attempts": self.max_attempts,
        }


class CaptchaSerializer(serializers.Serializer):
    """
    Serializer for CAPTCHA validation.
    """
    captcha_id = serializers.CharField()
    captcha_text = serializers.CharField(validators=[CaptchaValidator()])