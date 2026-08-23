"""Example serializer and viewset integration for DRF-CaptchaX."""

from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from .validator import CaptchaValidator


class UserRegistrationSerializer(serializers.Serializer):
    """Example registration serializer with paired CAPTCHA validation."""

    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    captcha_id = serializers.CharField()
    captcha_text = serializers.CharField()

    def validate(self, attrs):
        """Validate the CAPTCHA fields together."""
        CaptchaValidator().validate(attrs["captcha_text"], attrs["captcha_id"])
        return attrs


class RegistrationViewSet(viewsets.ViewSet):
    """Example viewset that rejects requests with invalid CAPTCHA data."""

    def create(self, request):
        """Validate registration input and return a sample success response."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"detail": "Registration successful"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
