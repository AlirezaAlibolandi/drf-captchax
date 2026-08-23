# DRF-CaptchaX

DRF-CaptchaX provides a lightweight CAPTCHA solution for Django REST Framework with in-process and Redis storage backends.

## Requirements

- Python 3.10+
- Django 5.2, 6.0, or 6.1
- Django REST Framework 3.18.x
- Pillow 10+

## Installation

```bash
pip install drf-captchax
```

For Redis-backed storage:

```bash
pip install "drf-captchax[redis]"
```

## Setup

Add the app and URLs:

```python
INSTALLED_APPS = [
    "rest_framework",
    "captchax",
]

urlpatterns = [
    path("captcha/", include("captchax.urls")),
]
```

The default endpoints are:

- `GET /captcha/generate/`
- `POST /captcha/validate/`

The validation request body is:

```json
{
  "captcha_id": "generated-id",
  "captcha_text": "ABCD23"
}
```

## Serializer integration

Use object-level validation because CAPTCHA validation needs both fields:

```python
from rest_framework import serializers
from captchax.validator import CaptchaValidator


class DemoSerializer(serializers.Serializer):
    username = serializers.CharField()
    captcha_id = serializers.CharField()
    captcha_text = serializers.CharField()

    def validate(self, attrs):
        CaptchaValidator().validate(attrs["captcha_text"], attrs["captcha_id"])
        return attrs
```

You can also use `CaptchaSerializer` directly for the two CAPTCHA fields.

## Configuration

```python
CAPTCHAX = {
    "LENGTH": 6,
    "CHARACTERS": "ABCDEFGHJKLMNPQRSTUVWXYZ23456789",
    "WIDTH": 200,
    "HEIGHT": 60,
    "FONT_SIZE": 36,
    "BACKGROUND_COLOR": "#ffffff",
    "TEXT_COLOR": "#000000",
    "NOISE_LEVEL": 20,
    "USE_LINES": True,
    "USE_DOTS": True,
    "TIMEOUT": 300,
    "CASE_SENSITIVE": False,
    "MAX_ATTEMPTS": 5,
    "BACKEND": "captchax.backend.memory.MemoryBackend",
    "BACKEND_OPTIONS": {},
}
```

The memory backend is process-local and intended for development, tests, or single-process deployments. Use Redis for multi-worker production deployments:

```python
CAPTCHAX = {
    "BACKEND": "captchax.backend.redis.RedisBackend",
    "REDIS_URL": "redis://localhost:6379/0",
    "REDIS_PREFIX": "captchax:",
}
```

A custom Redis client can be supplied through `REDIS_CLIENT`.

## Development

```bash
pip install -e ".[dev,redis]"
pytest
python -m build
```
