# DRF-CaptchaX

[![PyPI version](https://badge.fury.io/py/drf-captchax.svg)](https://badge.fury.io/py/drf-captchax)
[![Python Versions](https://img.shields.io/pypi/pyversions/drf-captchax.svg)](https://pypi.org/project/drf-captchax/)
[![Django Versions](https://img.shields.io/badge/django-3.2%2B-blue)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful and flexible CAPTCHA integration for Django REST Framework with multiple storage backends and customization options.

## Features

- 🚀 Easy integration with Django REST Framework
- 🎨 Highly customizable CAPTCHA generation
- 💾 Multiple storage backends (Memory, Redis)
- ✨ Simple validation process
- 🔒 Secure by design
- 📱 Mobile-friendly
- 🌐 Internationalization support
- ⚡ High performance
- 🧪 Comprehensive test suite

## Installation

```bash
pip install drf-captchax
```

## Quick Start

1. Add 'captchax' to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'captchax',
]
```

2. Include CAPTCHA URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('captcha/', include('captchax.urls')),
]
```

3. Configure CAPTCHA settings in your Django settings:

```python
CAPTCHAX = {
    # CAPTCHA Generation
    'LENGTH': 6,                    # Length of CAPTCHA text
    'WIDTH': 200,                   # Image width
    'HEIGHT': 60,                   # Image height
    'FONT_SIZE': 36,               # Font size
    'BACKGROUND_COLOR': '#ffffff',  # Background color
    'TEXT_COLOR': '#000000',       # Text color
    'NOISE_LEVEL': 20,             # Noise level (0-100)
    'USE_LINES': True,             # Add random lines
    'USE_DOTS': True,              # Add random dots
    
    # Validation
    'TIMEOUT': 300,                # CAPTCHA validity period in seconds
    'CASE_SENSITIVE': False,       # Case-sensitive validation
    'MAX_ATTEMPTS': 5,             # Maximum validation attempts
    
    # Storage Backend
    'BACKEND': 'captchax.backend.memory.MemoryBackend',  # Default backend
    # For Redis backend:
    # 'BACKEND': 'captchax.backend.redis.RedisBackend',
    # 'REDIS_URL': 'redis://localhost:6379/0',
    # 'REDIS_PREFIX': 'captchax:',
}
```

4. Use in your serializers:

```python
from rest_framework import serializers
from captchax.validator import CaptchaValidator

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    captcha_id = serializers.CharField()
    captcha_text = serializers.CharField(validators=[CaptchaValidator()])
```

5. Frontend Integration:

```html
<!-- Template -->
<form method="post" action="/api/register/">
    <!-- Your form fields -->
    <div class="captcha-container">
        <img id="captcha-image" alt="CAPTCHA">
        <button type="button" onclick="refreshCaptcha()">↻</button>
        <input type="hidden" name="captcha_id" id="captcha-id">
        <input type="text" name="captcha_text" required>
    </div>
</form>

<!-- JavaScript -->
<script>
function refreshCaptcha() {
    fetch('/captcha/generate/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('captcha-image').src = data.image;
            document.getElementById('captcha-id').value = data.captcha_id;
        });
}

// Refresh CAPTCHA on page load
document.addEventListener('DOMContentLoaded', refreshCaptcha);
</script>

<!-- Optional CSS -->
<style>
.captcha-container {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 15px 0;
}
</style>
```

## Advanced Usage

### Custom Validation

```python
from captchax.validator import CaptchaValidator

# Case-sensitive validation
validator = CaptchaValidator(case_sensitive=True)

# Custom maximum attempts
validator = CaptchaValidator(max_attempts=3)

# Custom backend
from captchax.backend.redis import RedisBackend
validator = CaptchaValidator(
    backend_class=RedisBackend,
    redis_url='redis://localhost:6379/0'
)
```

### Custom CAPTCHA Generation

```python
from captchax.captcha import CaptchaGenerator

generator = CaptchaGenerator(
    length=8,
    width=300,
    height=80,
    font_size=42,
    background_color='#f0f0f0',
    text_color='#333333',
    noise_level=30
)

captcha_id, image = generator.generate_image()
```

### Redis Backend Configuration

For production environments, it's recommended to use the Redis backend:

```python
CAPTCHAX = {
    'BACKEND': 'captchax.backend.redis.RedisBackend',
    'REDIS_URL': 'redis://localhost:6379/0',
    'REDIS_PREFIX': 'captchax:',
    # Other settings...
}
```

## API Endpoints

- `GET /captcha/generate/`: Generate a new CAPTCHA
  - Returns: `{"captcha_id": "...", "image": "data:image/png;base64,..."}`

- `POST /captcha/validate/`: Validate a CAPTCHA response
  - Data: `{"captcha_id": "...", "captcha_text": "..."}`
  - Returns: `200 OK` if valid, `400 Bad Request` if invalid

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=captchax
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

Please make sure to:
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Created and maintained by [Alireza Alibolandi](https://github.com/AlirezaAlibolandi).

## Support

- 📫 Report issues on [GitHub](https://github.com/AlirezaAlibolandi/drf-captchax/issues)
- 📚 Read the [documentation](https://drf-captchax.readthedocs.io/)
- 💬 Ask questions on [Stack Overflow](https://stackoverflow.com/questions/tagged/drf-captchax)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AlirezaAlibolandi/drf-captchax&type=Date)](https://star-history.com/#AlirezaAlibolandi/drf-captchax&Date)