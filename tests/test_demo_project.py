"""Tests for the included demo serializer."""

from captchax.backend.memory import MemoryBackend
from demo_project.api.views import DemoSerializer


def test_demo_serializer_valid():
    """Accept a correct CAPTCHA in the demo serializer."""
    MemoryBackend().store_captcha("id", "CODE", 300)
    serializer = DemoSerializer(
        data={"username": "u", "captcha_id": "id", "captcha_text": "CODE"}
    )
    assert serializer.is_valid(), serializer.errors


def test_demo_serializer_invalid():
    """Reject an incorrect CAPTCHA in the demo serializer."""
    MemoryBackend().store_captcha("id", "CODE", 300)
    serializer = DemoSerializer(
        data={"username": "u", "captcha_id": "id", "captcha_text": "WRONG"}
    )
    assert not serializer.is_valid()
