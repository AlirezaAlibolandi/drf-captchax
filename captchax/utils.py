"""
Utility functions for the CAPTCHA package.
"""

import base64
from io import BytesIO
from typing import Tuple
from PIL import Image
import uuid


def generate_captcha_id():
    return str(uuid.uuid4())


def image_to_base64(image: Image.Image, format: str = 'PNG') -> str:
    """
    Convert a PIL Image to base64 string.
    
    Args:
        image: PIL Image instance
        format: Image format (default: PNG)
        
    Returns:
        Base64 encoded image string
    """
    buffer = BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode()


def get_image_dimensions(width: int, height: int, max_width: int = 400, max_height: int = 200) -> Tuple[int, int]:
    """
    Calculate proportional image dimensions within maximum bounds.
    
    Args:
        width: Original width
        height: Original height
        max_width: Maximum allowed width
        max_height: Maximum allowed height
        
    Returns:
        Tuple of (new_width, new_height)
    """
    if width <= max_width and height <= max_height:
        return width, height
        
    ratio = min(max_width / width, max_height / height)
    return int(width * ratio), int(height * ratio)
