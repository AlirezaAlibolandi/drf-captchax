"""Test package for drf-captchax."""

# Ensure the demo project is importable when pytest-django loads settings
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "demo_project"))