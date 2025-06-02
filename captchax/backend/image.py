import base64
import io
import random
import string

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.conf import settings

from captchax.settings import DEFAULT_CAPTCHAX_CONFIG


class ImageCaptchaBackend:
    def __init__(self):
        user_cfg = getattr(settings, "CAPTCHAX_CONFIG", {})
        cfg = {**DEFAULT_CAPTCHAX_CONFIG, **user_cfg}

        self.length = cfg["LENGTH"]
        self.width = cfg["WIDTH"]
        self.height = cfg["HEIGHT"]
        self.font_size = cfg["FONT_SIZE"]
        self.font_path = cfg["FONT_PATH"]

    def generate_text(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=self.length))

    def generate_image(self, code: str) -> str:
        image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(self.font_path, self.font_size)
        char_spacing = self.width // (len(code) + 1)

        for i, char in enumerate(code):
            x = char_spacing * (i + 1) - self.font_size // 2 + random.randint(-5, 5)
            y = random.randint(5, 10)
            char_image = Image.new('RGBA', (self.font_size + 10, self.font_size + 10), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((5, 0), char, font=font, fill=(0, 0, 0))
            rotated = char_image.rotate(random.uniform(-25, 25), resample=Image.BICUBIC, expand=1)
            image.paste(rotated, (x, y), rotated)

        for _ in range(800):
            draw.point((random.randint(0, self.width), random.randint(0, self.height)),
                       fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))

        for _ in range(30):
            draw.line([(random.randint(0, self.width), random.randint(0, self.height)),
                       (random.randint(0, self.width), random.randint(0, self.height))],
                      fill=(120, 120, 120), width=1)

        image = image.filter(ImageFilter.SMOOTH)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
