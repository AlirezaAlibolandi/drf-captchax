"""Integration tests for public CAPTCHA endpoints."""

from rest_framework.test import APIClient

from captchax.backend.memory import MemoryBackend


def test_generate_and_validate_round_trip():
    """Generate a challenge and validate it through separate backend instances."""
    client = APIClient()
    generated = client.get("/captcha/generate/")
    assert generated.status_code == 200
    payload = generated.json()
    assert payload["image"].startswith("data:image/png;base64,")
    assert "no-store" in generated["Cache-Control"]

    captcha_id = payload["captcha_id"]
    text = MemoryBackend().get_captcha(captcha_id)
    assert text is not None

    validated = client.post(
        "/captcha/validate/",
        {"captcha_id": captcha_id, "captcha_text": text},
        format="json",
    )
    assert validated.status_code == 200
    assert MemoryBackend().get_captcha(captcha_id) is None


def test_validate_rejects_reuse():
    """Prevent replay after a successful validation."""
    backend = MemoryBackend()
    backend.store_captcha("test-id", "TEST123", 300)
    client = APIClient()

    first = client.post(
        "/captcha/validate/",
        {"captcha_id": "test-id", "captcha_text": "TEST123"},
        format="json",
    )
    second = client.post(
        "/captcha/validate/",
        {"captcha_id": "test-id", "captcha_text": "TEST123"},
        format="json",
    )
    assert first.status_code == 200
    assert second.status_code == 400


def test_validate_enforces_attempt_limit():
    """Delete a challenge when invalid attempts reach the configured limit."""
    backend = MemoryBackend()
    backend.store_captcha("test-id", "TEST123", 300)
    client = APIClient()

    responses = [
        client.post(
            "/captcha/validate/",
            {"captcha_id": "test-id", "captcha_text": "WRONG"},
            format="json",
        )
        for _ in range(5)
    ]

    assert all(response.status_code == 400 for response in responses)
    assert MemoryBackend().get_captcha("test-id") is None
