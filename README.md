# DRF-CaptchaX

![Tests](https://github.com/AlirezaAlibolandi/drf-captchax/actions/workflows/tests.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/drf-captchax.svg)](https://pypi.org/project/drf-captchax/)

DRF-CaptchaX provides a simple CAPTCHA solution for Django REST Framework.

## Installation

```bash
pip install drf-captchax
```

## Usage

Add `captchax` to `INSTALLED_APPS` and include its URLs:

```python
INSTALLED_APPS = [
    'rest_framework',
    'captchax',
]

urlpatterns = [
    path('captcha/', include('captchax.urls')),
]
```

Validate captcha responses in serializers:

```python
from rest_framework import serializers
from captchax.validator import CaptchaValidator

class DemoSerializer(serializers.Serializer):
    username = serializers.CharField()
    captcha_id = serializers.CharField()
    captcha_text = serializers.CharField(validators=[CaptchaValidator()])
```

## Development

Install dev dependencies and run the tests:

```bash
pip install -e .[dev]
pytest
```

## Release Automation

Pushes to `main` or tags starting with `v` automatically upload a new package to PyPI via GitHub Actions.

