"""
CAPTCHA image generation module.

This module provides functionality for generating CAPTCHA images
with customizable text, styling, and noise options.
"""

import os
import random
import string
import uuid
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from .settings import CAPTCHAX_CONFIG


def generate_text(length: Optional[int] = None) -> str:
    """
    Generate random CAPTCHA text.
    
    Args:
        length: Optional custom length for the text
        
    Returns:
        Random string for CAPTCHA
    """
    length = length or CAPTCHAX_CONFIG["LENGTH"]
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: Color in hex format (e.g. '#ffffff')
        
    Returns:
        Tuple of RGB values
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class CaptchaGenerator:
    """
    CAPTCHA image generator with customizable options.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the generator with custom settings.
        
        Args:
            **kwargs: Override default settings from CAPTCHAX_CONFIG
        """
        self.config = CAPTCHAX_CONFIG.copy()
        self.config.update(kwargs)
        
        if not os.path.exists(self.config["FONT_PATH"]):
            raise ValueError(f"Font file not found: {self.config['FONT_PATH']}")
            
        self.font = ImageFont.truetype(
            self.config["FONT_PATH"],
            size=self.config["FONT_SIZE"]
        )
        
    def _add_noise_dots(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        """Add random dots to the image."""
        noise_level = self.config["NOISE_LEVEL"]
        num_dots = int((width * height) * noise_level / 1000)
        
        for _ in range(num_dots):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill=self.config["TEXT_COLOR"])
            
    def _add_noise_lines(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        """Add random lines to the image."""
        noise_level = self.config["NOISE_LEVEL"]
        num_lines = int(noise_level / 10)
        
        for _ in range(num_lines):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=self.config["TEXT_COLOR"])
            
    def generate_image(self, text: Optional[str] = None) -> Tuple[str, Image.Image]:
        """
        Generate a CAPTCHA image.
        
        Args:
            text: Optional custom text for the CAPTCHA
            
        Returns:
            Tuple of (captcha_id, PIL Image)
        """
        text = text or generate_text(self.config["LENGTH"])
        width = self.config["WIDTH"]
        height = self.config["HEIGHT"]
        
        # Create image
        image = Image.new('RGB', (width, height), self.config["BACKGROUND_COLOR"])
        draw = ImageDraw.Draw(image)
        
        # Calculate text position
        text_width = draw.textlength(text, font=self.font)
        text_height = self.font.size
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Add noise
        if self.config["USE_DOTS"]:
            self._add_noise_dots(draw, width, height)
        if self.config["USE_LINES"]:
            self._add_noise_lines(draw, width, height)
            
        # Draw text
        draw.text((x, y), text, font=self.font, fill=hex_to_rgb(self.config["TEXT_COLOR"]))
        
        return str(uuid.uuid4()), image