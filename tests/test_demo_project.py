import pytest
from unittest.mock import patch
from demo_project.api.views import DemoSerializer
from captchax.validator import CaptchaValidator
from captchax.backend.memory import MemoryBackend

class SharedMemoryBackend(MemoryBackend):
    _shared = {}
    def __init__(self):
        self._storage = SharedMemoryBackend._shared

def test_demo_serializer_valid():
    backend = SharedMemoryBackend()
    backend.store_captcha('id', 'CODE', 300)
    with patch('demo_project.api.views.CaptchaValidator', lambda **kwargs: CaptchaValidator(backend_class=SharedMemoryBackend)):
        serializer = DemoSerializer(data={'username': 'u', 'captcha_id': 'id', 'captcha_text': 'CODE'})
        assert serializer.is_valid()

def test_demo_serializer_invalid():
    backend = SharedMemoryBackend()
    backend.store_captcha('id', 'CODE', 300)
    with patch('demo_project.api.views.CaptchaValidator', lambda **kwargs: CaptchaValidator(backend_class=SharedMemoryBackend)):
        serializer = DemoSerializer(data={'username': 'u', 'captcha_id': 'id', 'captcha_text': 'WRONG'})
        assert not serializer.is_valid()

