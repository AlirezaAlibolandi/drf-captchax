"""Compatibility image backend built on the primary CAPTCHA generator."""

from ..captcha import CaptchaGenerator, generate_text
from ..utils import image_to_base64


class ImageCaptchaBackend:
    """Generate CAPTCHA text and data-URI PNG images."""

    def __init__(self, **kwargs):
        """Initialize an image generator with optional setting overrides."""
        self.generator = CaptchaGenerator(**kwargs)

    def generate_text(self) -> str:
        """Generate CAPTCHA text using the configured length and alphabet."""
        return generate_text(
            self.generator.config["LENGTH"],
            self.generator.config["CHARACTERS"],
        )

    def generate_image(self, code: str) -> str:
        """Generate a base64 PNG data URI for the supplied CAPTCHA text."""
        _, image, _ = self.generator.generate_image(code)
        return f"data:image/png;base64,{image_to_base64(image)}"
