"""
Django REST Framework CAPTCHA configuration settings.

This module handles the configuration settings for the CAPTCHA system, including
image generation parameters, storage backend settings, and validation options.
"""

import os
from typing import Dict, Any, Optional
from django.conf import settings
import importlib.resources
import redis

# Default font path using importlib.resources
with importlib.resources.path("captchax.static.fonts", "dejavu-sans.ttf") as font_path:
    DEFAULT_FONT_PATH = str(font_path)

# Default configuration settings
DEFAULTS: Dict[str, Any] = {
    # CAPTCHA image settings
    "LENGTH": 6,  # Length of the CAPTCHA text
    "WIDTH": 200,  # Width of the generated image
    "HEIGHT": 60,  # Height of the generated image
    "FONT_SIZE": 36,  # Font size for the text
    "FONT_PATH": DEFAULT_FONT_PATH,  # Path to the font file
    
    # Image generation settings
    "BACKGROUND_COLOR": "#ffffff",  # Background color of the image
    "TEXT_COLOR": "#000000",  # Color of the CAPTCHA text
    "NOISE_LEVEL": 20,  # Level of noise/difficulty (0-100)
    "USE_LINES": True,  # Add random lines to the image
    "USE_DOTS": True,  # Add random dots to the image
    
    # Validation settings
    "TIMEOUT": 300,  # CAPTCHA validity period in seconds
    "CASE_SENSITIVE": False,  # Whether validation is case-sensitive
    "MAX_ATTEMPTS": 5,  # Maximum number of validation attempts
    
    # Storage backend settings
    "BACKEND": "captchax.backend.memory.MemoryBackend",  # Storage backend class
    "REDIS_URL": None,  # Redis connection URL for RedisBackend
    "REDIS_PREFIX": "captchax:",  # Prefix for Redis keys
    "REDIS_CLIENT": None,  # Custom Redis client instance
}

# Get user-defined settings
USER_SETTINGS = getattr(settings, "CAPTCHAX", {})

# Merge default and user settings
CAPTCHAX_CONFIG = DEFAULTS.copy()
CAPTCHAX_CONFIG.update(USER_SETTINGS)

def get_backend_class():
    """
    Get the configured storage backend class.
    
    Returns:
        The backend class specified in the settings.
    """
    from importlib import import_module
    
    backend_path = CAPTCHAX_CONFIG["BACKEND"]
    module_path, class_name = backend_path.rsplit(".", 1)
    
    module = import_module(module_path)
    return getattr(module, class_name)

def get_redis_client() -> Optional[redis.Redis]:
    """
    Get or create a Redis client instance based on configuration.
    
    Returns:
        Optional[redis.Redis]: Configured Redis client or None if not using Redis backend.
    """
    if CAPTCHAX_CONFIG["REDIS_CLIENT"]:
        return CAPTCHAX_CONFIG["REDIS_CLIENT"]
    
    if CAPTCHAX_CONFIG["REDIS_URL"]:
        return redis.from_url(CAPTCHAX_CONFIG["REDIS_URL"])
    
    return None
