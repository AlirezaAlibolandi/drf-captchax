"""Public package API for DRF-CaptchaX."""

from importlib import import_module

__version__ = "0.2.0"

_EXPORTS = {
    "CaptchaGenerator": ("captchax.captcha", "CaptchaGenerator"),
    "generate_text": ("captchax.captcha", "generate_text"),
    "CaptchaValidator": ("captchax.validator", "CaptchaValidator"),
    "CaptchaSerializer": ("captchax.validator", "CaptchaSerializer"),
    "CaptchaBackend": ("captchax.backend", "CaptchaBackend"),
    "MemoryBackend": ("captchax.backend.memory", "MemoryBackend"),
    "RedisBackend": ("captchax.backend.redis", "RedisBackend"),
}

__all__ = ["__version__", *_EXPORTS]


def __getattr__(name):
    """Lazily import public API attributes to avoid premature Django setup."""
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value
