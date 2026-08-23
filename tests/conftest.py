"""Shared pytest configuration."""

import os
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "demo_project"
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

from captchax.backend.memory import MemoryBackend


@pytest.fixture(autouse=True)
def clear_memory_backend():
    """Isolate tests that use the process-local memory backend."""
    MemoryBackend.clear()
    yield
    MemoryBackend.clear()
