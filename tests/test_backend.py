"""
Tests for CAPTCHA storage backends.
"""

import time
import pytest
import redis
from unittest.mock import MagicMock
from captchax.backend import CaptchaBackend
from captchax.backend.memory import MemoryBackend
from captchax.backend.redis import RedisBackend


class TestCaptchaBackend:
    """Test the abstract base class."""
    
    def test_abstract_methods(self):
        """Test that abstract methods raise NotImplementedError."""
        class TestBackend(CaptchaBackend):
            pass
            
        with pytest.raises(TypeError):
            TestBackend()


class TestMemoryBackend:
    """Test the memory backend implementation."""
    
    @pytest.fixture
    def backend(self):
        """Create a MemoryBackend instance."""
        return MemoryBackend()
        
    def test_store_and_get(self, backend):
        """Test storing and retrieving CAPTCHA."""
        backend.store_captcha("test-id", "TEST123", 300)
        assert backend.get_captcha("test-id") == "TEST123"
        
    def test_expiration(self, backend):
        """Test CAPTCHA expiration."""
        backend.store_captcha("test-id", "TEST123", 1)
        time.sleep(1.1)  # Wait for expiration
        assert backend.get_captcha("test-id") is None
        
    def test_delete(self, backend):
        """Test deleting CAPTCHA."""
        backend.store_captcha("test-id", "TEST123", 300)
        backend.delete_captcha("test-id")
        assert backend.get_captcha("test-id") is None
        
    def test_attempts(self, backend):
        """Test attempts counting."""
        backend.store_captcha("test-id", "TEST123", 300)
        assert backend.get_attempts("test-id") == 0
        
        backend.increment_attempts("test-id")
        assert backend.get_attempts("test-id") == 1
        
        backend.increment_attempts("test-id")
        assert backend.get_attempts("test-id") == 2


class TestRedisBackend:
    """Test the Redis backend implementation."""
    
    @pytest.fixture
    def redis_mock(self):
        """Create a mock Redis client."""
        client = MagicMock(spec=redis.Redis)
        client.get.return_value = None
        return client
        
    @pytest.fixture
    def backend(self, redis_mock):
        """Create a RedisBackend instance with mock client."""
        return RedisBackend(redis_client=redis_mock)
        
    def test_store_and_get(self, backend, redis_mock):
        """Test storing and retrieving CAPTCHA."""
        redis_mock.get.return_value = b"TEST123"
        
        backend.store_captcha("test-id", "TEST123", 300)
        assert backend.get_captcha("test-id") == "TEST123"
        
        # Verify Redis calls
        redis_mock.pipeline.assert_called_once()
        
    def test_delete(self, backend, redis_mock):
        """Test deleting CAPTCHA."""
        backend.delete_captcha("test-id")
        
        # Verify Redis calls
        redis_mock.pipeline.assert_called_once()
        
    def test_attempts(self, backend, redis_mock):
        """Test attempts counting."""
        redis_mock.get.return_value = b"2"
        redis_mock.incr.return_value = 3
        
        assert backend.get_attempts("test-id") == 2
        assert backend.increment_attempts("test-id") == 3