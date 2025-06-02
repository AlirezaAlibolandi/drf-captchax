"""
Django REST Framework CAPTCHA integration.

This package provides CAPTCHA support for Django REST Framework
with customizable generation, validation, and storage options.
"""

__version__ = "0.1.0"

from .captcha import CaptchaGenerator, generate_text
from .validator import CaptchaValidator, CaptchaSerializer
from .backend import CaptchaBackend
from .backend.memory import MemoryBackend
from .backend.redis import RedisBackend

__all__ = [
    'CaptchaGenerator',
    'generate_text',
    'CaptchaValidator',
    'CaptchaSerializer',
    'CaptchaBackend',
    'MemoryBackend',
    'RedisBackend',
]
