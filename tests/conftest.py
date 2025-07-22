"""
Pytest configuration for Django tests.
"""

import os
import sys
from pathlib import Path
import django
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "demo_project"))

# Configure Django settings for tests
def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    settings.DEBUG = False
    django.setup() 
