"""
Django app configuration for CAPTCHA.
"""

from django.apps import AppConfig


class CaptchaxConfig(AppConfig):
    """
    Configuration class for the CAPTCHA app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'captchax'
    verbose_name = 'DRF CAPTCHA' 