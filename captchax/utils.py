"""Utility functions for DRF-CaptchaX."""

import base64
import uuid
from io import BytesIO
from typing import Tuple

from PIL import Image


def generate_captcha_id() -> str:
    """Return a random UUID CAPTCHA identifier."""
    return str(uuid.uuid4())


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Encode a Pillow image as a base64 string."""
    buffer = BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def get_image_dimensions(
    width: int,
    height: int,
    max_width: int = 400,
    max_height: int = 200,
) -> Tuple[int, int]:
    """Scale dimensions proportionally to fit within the supplied bounds."""
    if min(width, height, max_width, max_height) <= 0:
        raise ValueError("Image dimensions must be positive")
    if width <= max_width and height <= max_height:
        return width, height
    ratio = min(max_width / width, max_height / height)
    return max(1, int(width * ratio)), max(1, int(height * ratio))
