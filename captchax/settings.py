"""Configuration helpers for DRF-CaptchaX."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

DEFAULT_FONT_PATH = str(
    Path(__file__).resolve().parent / "static" / "fonts" / "dejavu-sans.ttf"
)

DEFAULTS: dict[str, Any] = {
    "LENGTH": 6,
    "CHARACTERS": "ABCDEFGHJKLMNPQRSTUVWXYZ23456789",
    "WIDTH": 200,
    "HEIGHT": 60,
    "FONT_SIZE": 36,
    "FONT_PATH": DEFAULT_FONT_PATH,
    "BACKGROUND_COLOR": "#ffffff",
    "TEXT_COLOR": "#000000",
    "NOISE_LEVEL": 20,
    "USE_LINES": True,
    "USE_DOTS": True,
    "TIMEOUT": 300,
    "CASE_SENSITIVE": False,
    "MAX_ATTEMPTS": 5,
    "BACKEND": "captchax.backend.memory.MemoryBackend",
    "BACKEND_OPTIONS": {},
    "REDIS_URL": None,
    "REDIS_PREFIX": "captchax:",
    "REDIS_CLIENT": None,
}


def get_config() -> dict[str, Any]:
    """Return the merged CAPTCHA configuration."""
    user_settings = getattr(settings, "CAPTCHAX", {})
    if not isinstance(user_settings, Mapping):
        raise ImproperlyConfigured("CAPTCHAX must be a mapping")

    config = DEFAULTS.copy()
    config.update(dict(user_settings))
    return config


CAPTCHAX_CONFIG = get_config()


def get_backend_class():
    """Return the configured CAPTCHA backend class."""
    backend_path = get_config()["BACKEND"]
    if not isinstance(backend_path, str) or "." not in backend_path:
        raise ImproperlyConfigured("CAPTCHAX['BACKEND'] must be a dotted class path")

    try:
        backend_class = import_string(backend_path)
    except ImportError as exc:
        raise ImproperlyConfigured(
            f"Unable to import CAPTCHA backend '{backend_path}'"
        ) from exc

    from .backend import CaptchaBackend

    if not isinstance(backend_class, type) or not issubclass(backend_class, CaptchaBackend):
        raise ImproperlyConfigured(
            f"CAPTCHA backend '{backend_path}' must subclass CaptchaBackend"
        )
    return backend_class


def get_backend_instance():
    """Create the configured CAPTCHA backend instance."""
    config = get_config()
    options = config.get("BACKEND_OPTIONS", {})
    if not isinstance(options, Mapping):
        raise ImproperlyConfigured("CAPTCHAX['BACKEND_OPTIONS'] must be a mapping")
    return get_backend_class()(**dict(options))


def get_redis_client() -> Optional[Any]:
    """Return the configured Redis client, creating one from REDIS_URL if needed."""
    config = get_config()
    if config["REDIS_CLIENT"] is not None:
        return config["REDIS_CLIENT"]

    redis_url = config["REDIS_URL"]
    if not redis_url:
        return None

    try:
        import redis
    except ImportError as exc:
        raise ImproperlyConfigured(
            "Redis support requires the 'redis' extra: pip install drf-captchax[redis]"
        ) from exc

    return redis.from_url(redis_url)
