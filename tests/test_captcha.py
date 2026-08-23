"""Tests for CAPTCHA image generation."""

import base64

import pytest
from PIL import Image

from captchax.backend.image import ImageCaptchaBackend
from captchax.captcha import CaptchaGenerator, generate_text, hex_to_rgb
from captchax.settings import get_config


def test_generate_text():
    """Generate text using default and custom lengths."""
    config = get_config()
    text = generate_text()
    assert len(text) == config["LENGTH"]
    assert set(text) <= set(config["CHARACTERS"])
    assert len(generate_text(8)) == 8


def test_generate_text_rejects_invalid_values():
    """Reject invalid lengths and alphabets."""
    with pytest.raises(ValueError, match="positive integer"):
        generate_text(0)
    with pytest.raises(ValueError, match="at least two"):
        generate_text(4, "A")


def test_hex_to_rgb():
    """Parse supported Pillow color values."""
    assert hex_to_rgb("#ffffff") == (255, 255, 255)
    assert hex_to_rgb("black") == (0, 0, 0)
    with pytest.raises(ValueError, match="Invalid color"):
        hex_to_rgb("not-a-color")


def test_captcha_generator_init():
    """Initialize default and overridden generator settings."""
    generator = CaptchaGenerator()
    assert generator.config["LENGTH"] == get_config()["LENGTH"]
    assert generator.font is not None

    generator = CaptchaGenerator(LENGTH=8, WIDTH=300)
    assert generator.config["LENGTH"] == 8
    assert generator.config["WIDTH"] == 300


def test_captcha_generator_image():
    """Generate correctly sized images and preserve supplied text."""
    generator = CaptchaGenerator()
    captcha_id, image, text = generator.generate_image()
    assert captcha_id
    assert text
    assert isinstance(image, Image.Image)
    assert image.size == (get_config()["WIDTH"], get_config()["HEIGHT"])

    _, custom_image, returned_text = generator.generate_image("TEST123")
    assert returned_text == "TEST123"
    assert isinstance(custom_image, Image.Image)


def test_captcha_generator_invalid_config():
    """Reject missing fonts and invalid dimensions or noise."""
    with pytest.raises(ValueError, match="Font file not found"):
        CaptchaGenerator(FONT_PATH="/nonexistent/font.ttf")
    with pytest.raises(ValueError, match="WIDTH"):
        CaptchaGenerator(WIDTH=0)
    with pytest.raises(ValueError, match="NOISE_LEVEL"):
        CaptchaGenerator(NOISE_LEVEL=101)


def test_compatibility_image_backend():
    """Keep the legacy image backend functional."""
    backend = ImageCaptchaBackend(LENGTH=4)
    text = backend.generate_text()
    data_uri = backend.generate_image(text)
    prefix, encoded = data_uri.split(",", 1)
    assert prefix == "data:image/png;base64"
    assert base64.b64decode(encoded).startswith(b"\x89PNG")
