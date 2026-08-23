"""Tests for CAPTCHA validation."""

import threading

import pytest
from rest_framework import serializers

from captchax.backend.memory import MemoryBackend
from captchax.validator import CaptchaSerializer, CaptchaValidator


@pytest.fixture
def validator():
    """Return a validator backed by in-process storage."""
    return CaptchaValidator(backend_class=MemoryBackend)


def test_validator_init():
    """Apply defaults and explicit validation settings."""
    validator = CaptchaValidator()
    assert validator.case_sensitive is False
    assert validator.max_attempts == 5
    assert isinstance(validator.backend, MemoryBackend)

    custom = CaptchaValidator(case_sensitive=True, max_attempts=3)
    assert custom.case_sensitive is True
    assert custom.max_attempts == 3

    with pytest.raises(ValueError, match="positive integer"):
        CaptchaValidator(max_attempts=0)


def test_validator_validate_success(validator):
    """Consume a CAPTCHA after successful validation."""
    validator.backend.store_captcha("test-id", "TEST123", 300)
    assert validator.validate("TEST123", "test-id") is True
    assert validator.backend.get_captcha("test-id") is None


def test_validator_validate_case_insensitive(validator):
    """Compare text case-insensitively by default."""
    validator.backend.store_captcha("test-id", "TEST123", 300)
    assert validator.validate("test123", "test-id") is True


def test_validator_validate_case_sensitive():
    """Respect case-sensitive mode."""
    validator = CaptchaValidator(case_sensitive=True, backend_class=MemoryBackend)
    validator.backend.store_captcha("test-id", "TEST123", 300)

    with pytest.raises(serializers.ValidationError, match="Invalid CAPTCHA response"):
        validator.validate("test123", "test-id")

    assert validator.validate("TEST123", "test-id") is True


def test_validator_max_attempts():
    """Invalidate and remove CAPTCHA after the configured attempt limit."""
    validator = CaptchaValidator(max_attempts=3, backend_class=MemoryBackend)
    validator.backend.store_captcha("test-id", "TEST123", 300)

    for _ in range(2):
        with pytest.raises(serializers.ValidationError, match="Invalid CAPTCHA response"):
            validator.validate("WRONG", "test-id")

    with pytest.raises(serializers.ValidationError, match="Maximum CAPTCHA attempts exceeded"):
        validator.validate("WRONG", "test-id")

    assert validator.backend.get_captcha("test-id") is None


def test_validator_rejects_missing_inputs(validator):
    """Reject missing CAPTCHA identifiers and responses."""
    with pytest.raises(serializers.ValidationError, match="ID is required"):
        validator.validate("TEST", None)
    with pytest.raises(serializers.ValidationError, match="response is required"):
        validator.validate("", "test-id")


def test_serializer_validates_pair():
    """Validate captcha_id and captcha_text together inside the serializer."""
    backend = MemoryBackend()
    backend.store_captcha("test-id", "TEST123", 300)
    validator = CaptchaValidator(backend_class=MemoryBackend)
    serializer = CaptchaSerializer(
        data={"captcha_id": "test-id", "captcha_text": "TEST123"},
        context={"captcha_validator": validator},
    )
    assert serializer.is_valid(), serializer.errors


def test_serializer_rejects_invalid_pair():
    """Return serializer errors for a wrong CAPTCHA response."""
    backend = MemoryBackend()
    backend.store_captcha("test-id", "TEST123", 300)
    validator = CaptchaValidator(backend_class=MemoryBackend)
    serializer = CaptchaSerializer(
        data={"captcha_id": "test-id", "captcha_text": "WRONG"},
        context={"captcha_validator": validator},
    )
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors


def test_serializer_level_validator_call(validator):
    """Support CaptchaValidator as a serializer-level validator."""
    validator.backend.store_captcha("test-id", "TEST123", 300)
    validator({"captcha_id": "test-id", "captcha_text": "TEST123"})


def test_concurrent_success_is_consumed_once():
    """Allow only one successful consumer for the same CAPTCHA."""
    validator = CaptchaValidator(backend_class=MemoryBackend)
    validator.backend.store_captcha("test-id", "TEST123", 300)
    barrier = threading.Barrier(8)
    results = []
    lock = threading.Lock()

    def worker():
        barrier.wait()
        try:
            validator.validate("TEST123", "test-id")
            result = True
        except serializers.ValidationError:
            result = False
        with lock:
            results.append(result)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count(True) == 1
