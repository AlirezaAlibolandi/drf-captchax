"""
Pytest configuration for Django tests.
"""

import os
import django
from django.conf import settings

# Configure Django settings for tests
def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    settings.DEBUG = False
    django.setup() 