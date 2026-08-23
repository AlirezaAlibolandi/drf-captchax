"""CAPTCHA validation primitives for Django REST Framework."""

import hmac
from collections.abc import Mapping
from typing import Any, Optional

from rest_framework import serializers

from .settings import get_backend_instance, get_config


class CaptchaValidator:
    """Validate CAPTCHA text against a configured storage backend."""

    def __init__(
        self,
        case_sensitive: Optional[bool] = None,
        max_attempts: Optional[int] = None,
        backend_class=None,
        **backend_kwargs,
    ):
        """Initialize validation policy and backend state."""
        config = get_config()
        self.case_sensitive = (
            config["CASE_SENSITIVE"] if case_sensitive is None else case_sensitive
        )
        self.max_attempts = (
            config["MAX_ATTEMPTS"] if max_attempts is None else max_attempts
        )
        if not isinstance(self.max_attempts, int) or self.max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
        if backend_class is None:
            self.backend = get_backend_instance()
        else:
            self.backend = backend_class(**backend_kwargs)

    def __call__(self, value: Any) -> None:
        """Validate serializer-level attrs containing captcha_id and captcha_text."""
        if not isinstance(value, Mapping):
            raise serializers.ValidationError(
                "CaptchaValidator must receive both captcha_id and captcha_text"
            )
        self.validate(value.get("captcha_text"), value.get("captcha_id"))

    def validate(
        self,
        captcha_text: str,
        captcha_id: Optional[str] = None,
        request=None,
    ) -> bool:
        """Validate a CAPTCHA response and consume it on success."""
        if captcha_id is None and request is not None and hasattr(request, "data"):
            captcha_id = request.data.get("captcha_id")

        if not isinstance(captcha_id, str) or not captcha_id.strip():
            raise serializers.ValidationError("CAPTCHA ID is required")
        if not isinstance(captcha_text, str) or not captcha_text.strip():
            raise serializers.ValidationError("CAPTCHA response is required")

        captcha_id = captcha_id.strip()
        attempts = self.backend.get_attempts(captcha_id)
        if attempts >= self.max_attempts:
            self.backend.delete_captcha(captcha_id)
            raise serializers.ValidationError("Maximum CAPTCHA attempts exceeded")

        stored_text = self.backend.get_captcha(captcha_id)
        if stored_text is None:
            self.backend.delete_captcha(captcha_id)
            raise serializers.ValidationError("CAPTCHA has expired or is invalid")

        expected = stored_text if self.case_sensitive else stored_text.casefold()
        received = captcha_text if self.case_sensitive else captcha_text.casefold()
        valid = hmac.compare_digest(expected.encode("utf-8"), received.encode("utf-8"))

        if valid:
            consumed_text = self.backend.consume_captcha(captcha_id)
            if consumed_text is None:
                raise serializers.ValidationError("CAPTCHA has expired or is invalid")
            consumed_expected = (
                consumed_text if self.case_sensitive else consumed_text.casefold()
            )
            if not hmac.compare_digest(
                consumed_expected.encode("utf-8"),
                received.encode("utf-8"),
            ):
                raise serializers.ValidationError("CAPTCHA has expired or is invalid")
            return True

        attempts = self.backend.increment_attempts(captcha_id)
        if attempts >= self.max_attempts:
            self.backend.delete_captcha(captcha_id)
            raise serializers.ValidationError("Maximum CAPTCHA attempts exceeded")
        raise serializers.ValidationError("Invalid CAPTCHA response")

    def get_validation_data(self) -> dict[str, Any]:
        """Return the active validation policy."""
        return {
            "case_sensitive": self.case_sensitive,
            "max_attempts": self.max_attempts,
        }


class CaptchaSerializer(serializers.Serializer):
    """Validate a CAPTCHA id and response pair."""

    captcha_id = serializers.CharField(trim_whitespace=True)
    captcha_text = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        """Validate both CAPTCHA fields together."""
        validator = self.context.get("captcha_validator")
        if validator is None:
            validator = CaptchaValidator()
        validator.validate(attrs["captcha_text"], attrs["captcha_id"])
        return attrs
