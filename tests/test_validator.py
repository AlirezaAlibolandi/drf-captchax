"""
Tests for CAPTCHA validation functionality.
"""

import pytest
from django.test import RequestFactory
from rest_framework.exceptions import ValidationError
from captchax.validator import CaptchaValidator, CaptchaSerializer
from captchax.backend.memory import MemoryBackend


@pytest.fixture
def validator():
    """Create a CaptchaValidator instance."""
    return CaptchaValidator(backend_class=MemoryBackend)


@pytest.fixture
def backend(validator):
    """Get the backend instance."""
    return validator.backend


@pytest.fixture
def request_factory():
    """Create a RequestFactory instance."""
    return RequestFactory()


def test_validator_init():
    """Test validator initialization."""
    validator = CaptchaValidator()
    assert validator.case_sensitive is False
    assert validator.max_attempts == 5
    assert isinstance(validator.backend, MemoryBackend)
    
    # Test custom settings
    validator = CaptchaValidator(case_sensitive=True, max_attempts=3)
    assert validator.case_sensitive is True
    assert validator.max_attempts == 3


def test_validator_validate_success(validator, backend, request_factory):
    """Test successful validation."""
    captcha_id = "test-id"
    captcha_text = "TEST123"
    
    # Store CAPTCHA
    backend.store_captcha(captcha_id, captcha_text, 300)
    
    # Create request with validation data
    request = request_factory.post('/', {
        'captcha_id': captcha_id,
        'captcha_text': captcha_text,
    })
    
    # Validate
    assert validator.validate(captcha_text, captcha_id, request) is True
    
    # Check CAPTCHA was deleted
    assert backend.get_captcha(captcha_id) is None


def test_validator_validate_case_insensitive(validator, backend):
    """Test case-insensitive validation."""
    captcha_id = "test-id"
    backend.store_captcha(captcha_id, "TEST123", 300)
    
    # Should pass with different case
    assert validator.validate("test123", captcha_id) is True


def test_validator_validate_case_sensitive():
    """Test case-sensitive validation."""
    validator = CaptchaValidator(case_sensitive=True, backend_class=MemoryBackend)
    captcha_id = "test-id"
    validator.backend.store_captcha(captcha_id, "TEST123", 300)
    
    # Should fail with different case
    with pytest.raises(ValidationError):
        validator.validate("test123", captcha_id)


def test_validator_max_attempts(validator, backend):
    """Test maximum attempts limit."""
    captcha_id = "test-id"
    backend.store_captcha(captcha_id, "TEST123", 300)
    
    # Make max_attempts invalid attempts
    for _ in range(validator.max_attempts):
        with pytest.raises(ValidationError):
            validator.validate("WRONG", captcha_id)
            
    # Next attempt should fail with max attempts error
    with pytest.raises(ValidationError, match="Maximum CAPTCHA attempts exceeded"):
        validator.validate("TEST123", captcha_id)


def test_serializer():
    """Test CaptchaSerializer."""
    serializer = CaptchaSerializer(data={
        'captcha_id': 'test-id',
        'captcha_text': 'TEST123',
    })
    
    assert serializer.is_valid() is False  # Should fail without stored CAPTCHA