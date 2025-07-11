"""Tests for CAPTCHA generation functionality."""

import pytest
from PIL import Image

from captchax.captcha import CaptchaGenerator, generate_text
from captchax.settings import CAPTCHAX_CONFIG


def test_generate_text():
    """Test CAPTCHA text generation."""
    text = generate_text()
    assert len(text) == CAPTCHAX_CONFIG['LENGTH']
    assert text.isupper()
    assert all(c.isalnum() for c in text)

    custom_length = 8
    text = generate_text(custom_length)
    assert len(text) == custom_length


def test_captcha_generator_init():
    """Test CaptchaGenerator initialization."""
    generator = CaptchaGenerator()
    assert generator.config['LENGTH'] == CAPTCHAX_CONFIG['LENGTH']
    assert generator.font is not None

    custom_config = {'LENGTH': 8, 'WIDTH': 300}
    generator = CaptchaGenerator(**custom_config)
    assert generator.config['LENGTH'] == 8
    assert generator.config['WIDTH'] == 300


def test_captcha_generator_image():
    """Test CAPTCHA image generation."""
    generator = CaptchaGenerator()

    captcha_id, image, text = generator.generate_image()
    assert isinstance(captcha_id, str)
    assert len(captcha_id) > 0
    assert isinstance(image, Image.Image)
    assert image.size == (CAPTCHAX_CONFIG['WIDTH'], CAPTCHAX_CONFIG['HEIGHT'])

    custom_text = "TEST123"
    captcha_id, image, returned_text = generator.generate_image(custom_text)
    assert returned_text == custom_text
    assert isinstance(image, Image.Image)
    assert image.size == (CAPTCHAX_CONFIG['WIDTH'], CAPTCHAX_CONFIG['HEIGHT'])


def test_captcha_generator_invalid_font():
    """Test CaptchaGenerator with invalid font path."""
    with pytest.raises(ValueError):        CaptchaGenerator(FONT_PATH="/nonexistent/font.ttf")
