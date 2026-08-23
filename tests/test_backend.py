"""Tests for CAPTCHA storage backends."""

from unittest.mock import MagicMock

import pytest

from captchax.backend import CaptchaBackend
from captchax.backend.memory import MemoryBackend
from captchax.backend.redis import RedisBackend


class TestCaptchaBackend:
    """Test the abstract storage interface."""

    def test_abstract_methods(self):
        """Ensure incomplete backend implementations cannot be instantiated."""
        class TestBackend(CaptchaBackend):
            """Incomplete backend used to verify abstract methods."""

        with pytest.raises(TypeError):
            TestBackend()


class TestMemoryBackend:
    """Test in-process storage behavior."""

    def test_store_and_get(self):
        """Store and retrieve a CAPTCHA."""
        backend = MemoryBackend()
        backend.store_captcha("test-id", "TEST123", 300)
        assert backend.get_captcha("test-id") == "TEST123"

    def test_instances_share_state(self):
        """Share generated CAPTCHA state across backend instances."""
        first = MemoryBackend()
        second = MemoryBackend()
        first.store_captcha("test-id", "TEST123", 300)
        assert second.get_captcha("test-id") == "TEST123"

    def test_expiration(self, monkeypatch):
        """Expire entries without a real-time sleep."""
        clock = iter([100.0, 100.0, 102.0])
        monkeypatch.setattr("captchax.backend.memory.time.monotonic", lambda: next(clock))
        backend = MemoryBackend()
        backend.store_captcha("test-id", "TEST123", 1)
        assert backend.get_captcha("test-id") is None

    def test_delete(self):
        """Delete CAPTCHA state."""
        backend = MemoryBackend()
        backend.store_captcha("test-id", "TEST123", 300)
        backend.delete_captcha("test-id")
        assert backend.get_captcha("test-id") is None

    def test_consume_is_one_time(self):
        """Atomically consume CAPTCHA state once."""
        backend = MemoryBackend()
        backend.store_captcha("test-id", "TEST123", 300)
        assert backend.consume_captcha("test-id") == "TEST123"
        assert backend.consume_captcha("test-id") is None

    def test_attempts(self):
        """Increment attempts atomically."""
        backend = MemoryBackend()
        backend.store_captcha("test-id", "TEST123", 300)
        assert backend.get_attempts("test-id") == 0
        assert backend.increment_attempts("test-id") == 1
        assert backend.increment_attempts("test-id") == 2
        assert backend.get_attempts("test-id") == 2


class TestRedisBackend:
    """Test Redis backend calls without a live Redis service."""

    @pytest.fixture
    def redis_mock(self):
        """Return a Redis-like mock client."""
        client = MagicMock()
        client.get.return_value = None
        return client

    @pytest.fixture
    def backend(self, redis_mock):
        """Return a backend using the mock Redis client."""
        return RedisBackend(redis_client=redis_mock)

    def test_store(self, backend, redis_mock):
        """Store CAPTCHA and attempts with one pipeline."""
        pipe = redis_mock.pipeline.return_value
        backend.store_captcha("test-id", "TEST123", 300)
        pipe.setex.assert_any_call("captchax:captcha:test-id", 300, "TEST123")
        pipe.setex.assert_any_call("captchax:attempts:test-id", 300, 0)
        pipe.execute.assert_called_once_with()

    def test_get_supports_bytes_and_strings(self, backend, redis_mock):
        """Handle Redis clients with or without decode_responses."""
        redis_mock.get.return_value = b"TEST123"
        assert backend.get_captcha("test-id") == "TEST123"
        redis_mock.get.return_value = "TEST456"
        assert backend.get_captcha("test-id") == "TEST456"

    def test_delete(self, backend, redis_mock):
        """Delete both keys through a pipeline."""
        pipe = redis_mock.pipeline.return_value
        backend.delete_captcha("test-id")
        pipe.delete.assert_any_call("captchax:captcha:test-id")
        pipe.delete.assert_any_call("captchax:attempts:test-id")
        pipe.execute.assert_called_once_with()

    def test_consume(self, backend, redis_mock):
        """Atomically consume CAPTCHA state with a Redis script."""
        redis_mock.eval.return_value = b"TEST123"
        assert backend.consume_captcha("test-id") == "TEST123"
        redis_mock.eval.assert_called_once()

    def test_attempts(self, backend, redis_mock):
        """Read and increment attempts while preserving TTL."""
        redis_mock.get.return_value = b"2"
        assert backend.get_attempts("test-id") == 2

        pipe = redis_mock.pipeline.return_value
        pipe.execute.return_value = [3, 120]
        assert backend.increment_attempts("test-id") == 3
        pipe.incr.assert_called_once_with("captchax:attempts:test-id")
        pipe.ttl.assert_called_once_with("captchax:captcha:test-id")
        redis_mock.expire.assert_called_once_with("captchax:attempts:test-id", 120)

    def test_increment_removes_orphan_attempt_key(self, backend, redis_mock):
        """Remove an attempts key when its CAPTCHA key no longer exists."""
        pipe = redis_mock.pipeline.return_value
        pipe.execute.return_value = [1, -2]
        assert backend.increment_attempts("test-id") == 0
        redis_mock.delete.assert_called_once_with("captchax:attempts:test-id")
