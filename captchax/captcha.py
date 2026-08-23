"""CAPTCHA text and image generation."""

import random
import secrets
import uuid
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageColor, ImageDraw, ImageFont

from .settings import get_config

_RANDOM = random.SystemRandom()


def generate_text(length: Optional[int] = None, characters: Optional[str] = None) -> str:
    """Generate cryptographically strong random CAPTCHA text."""
    config = get_config()
    text_length = config["LENGTH"] if length is None else length
    alphabet = config["CHARACTERS"] if characters is None else characters

    if not isinstance(text_length, int) or text_length <= 0:
        raise ValueError("CAPTCHA length must be a positive integer")
    if not isinstance(alphabet, str) or len(alphabet) < 2:
        raise ValueError("CAPTCHA characters must contain at least two characters")

    return "".join(secrets.choice(alphabet) for _ in range(text_length))


def hex_to_rgb(color: str) -> Tuple[int, int, int]:
    """Convert a Pillow-compatible color string to an RGB tuple."""
    try:
        rgb = ImageColor.getrgb(color)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid color value: {color!r}") from exc
    if len(rgb) == 4:
        return rgb[:3]
    return rgb


class CaptchaGenerator:
    """Generate CAPTCHA images using configurable dimensions, font, and noise."""

    def __init__(self, **kwargs):
        """Initialize the generator using project settings plus local overrides."""
        self.config = get_config()
        self.config.update(kwargs)
        self._validate_config()
        self.text_color = hex_to_rgb(self.config["TEXT_COLOR"])
        self.background_color = hex_to_rgb(self.config["BACKGROUND_COLOR"])
        self.font = ImageFont.truetype(
            self.config["FONT_PATH"],
            size=self.config["FONT_SIZE"],
        )

    def _validate_config(self) -> None:
        """Validate settings that can otherwise fail deep inside Pillow."""
        for key in ("WIDTH", "HEIGHT", "FONT_SIZE", "LENGTH"):
            value = self.config[key]
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{key} must be a positive integer")

        noise_level = self.config["NOISE_LEVEL"]
        if not isinstance(noise_level, (int, float)) or not 0 <= noise_level <= 100:
            raise ValueError("NOISE_LEVEL must be between 0 and 100")

        font_path = Path(self.config["FONT_PATH"])
        if not font_path.is_file():
            raise ValueError(f"Font file not found: {font_path}")

        hex_to_rgb(self.config["TEXT_COLOR"])
        hex_to_rgb(self.config["BACKGROUND_COLOR"])

    def _add_noise_dots(
        self,
        draw: ImageDraw.ImageDraw,
        width: int,
        height: int,
    ) -> None:
        """Add random dots to the image."""
        num_dots = int((width * height) * self.config["NOISE_LEVEL"] / 1000)
        for _ in range(num_dots):
            draw.point(
                (_RANDOM.randrange(width), _RANDOM.randrange(height)),
                fill=self.text_color,
            )

    def _add_noise_lines(
        self,
        draw: ImageDraw.ImageDraw,
        width: int,
        height: int,
    ) -> None:
        """Add random lines to the image."""
        num_lines = int(self.config["NOISE_LEVEL"] / 10)
        for _ in range(num_lines):
            draw.line(
                [
                    (_RANDOM.randrange(width), _RANDOM.randrange(height)),
                    (_RANDOM.randrange(width), _RANDOM.randrange(height)),
                ],
                fill=self.text_color,
            )

    def generate_image(self, text: Optional[str] = None) -> Tuple[str, Image.Image, str]:
        """Return a CAPTCHA id, generated Pillow image, and expected text."""
        if text is None:
            text = generate_text(self.config["LENGTH"], self.config["CHARACTERS"])
        if not isinstance(text, str) or not text:
            raise ValueError("CAPTCHA text must be a non-empty string")

        width = self.config["WIDTH"]
        height = self.config["HEIGHT"]
        image = Image.new("RGB", (width, height), self.background_color)
        draw = ImageDraw.Draw(image)

        if self.config["USE_DOTS"]:
            self._add_noise_dots(draw, width, height)
        if self.config["USE_LINES"]:
            self._add_noise_lines(draw, width, height)

        left, top, right, bottom = draw.textbbox((0, 0), text, font=self.font)
        text_width = right - left
        text_height = bottom - top
        x = (width - text_width) / 2 - left
        y = (height - text_height) / 2 - top
        draw.text((x, y), text, font=self.font, fill=self.text_color)

        return str(uuid.uuid4()), image, text
