"""Tests for dynamic project configuration."""

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from captchax.backend.memory import MemoryBackend
from captchax.settings import get_backend_class, get_backend_instance, get_config


def test_get_config_applies_override_settings():
    """Read CAPTCHAX dynamically so override_settings works after import."""
    with override_settings(CAPTCHAX={"LENGTH": 9}):
        assert get_config()["LENGTH"] == 9


def test_backend_factory():
    """Resolve and instantiate the configured backend."""
    assert get_backend_class() is MemoryBackend
    assert isinstance(get_backend_instance(), MemoryBackend)


def test_invalid_backend_configuration():
    """Raise useful configuration errors for invalid backend paths."""
    with override_settings(CAPTCHAX={"BACKEND": "missing"}):
        with pytest.raises(ImproperlyConfigured, match="dotted class path"):
            get_backend_class()
