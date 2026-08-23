"""Tests for package utilities."""

import base64
import uuid

import pytest
from PIL import Image

from captchax.utils import generate_captcha_id, get_image_dimensions, image_to_base64


def test_generate_captcha_id():
    """Generate a valid UUID string."""
    assert uuid.UUID(generate_captcha_id())


def test_image_to_base64():
    """Encode a PNG image."""
    encoded = image_to_base64(Image.new("RGB", (2, 2)))
    assert base64.b64decode(encoded).startswith(b"\x89PNG")


def test_get_image_dimensions():
    """Preserve or proportionally resize image dimensions."""
    assert get_image_dimensions(100, 50) == (100, 50)
    assert get_image_dimensions(800, 400, 400, 200) == (400, 200)
    with pytest.raises(ValueError, match="positive"):
        get_image_dimensions(0, 100)
