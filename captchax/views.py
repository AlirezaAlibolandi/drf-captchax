"""HTTP endpoints for CAPTCHA generation and validation."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .captcha import CaptchaGenerator
from .settings import get_backend_instance, get_config
from .utils import image_to_base64
from .validator import CaptchaSerializer


class GenerateCaptchaView(APIView):
    """Generate and persist a new CAPTCHA challenge."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        """Return a new CAPTCHA identifier and PNG data URI."""
        generator = CaptchaGenerator()
        captcha_id, image, text = generator.generate_image()
        get_backend_instance().store_captcha(
            captcha_id,
            text,
            get_config()["TIMEOUT"],
        )
        response = Response(
            {
                "captcha_id": captcha_id,
                "image": f"data:image/png;base64,{image_to_base64(image)}",
            }
        )
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        return response


class ValidateCaptchaView(APIView):
    """Validate and consume a CAPTCHA challenge."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        """Return success when the supplied CAPTCHA pair is valid."""
        serializer = CaptchaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": "CAPTCHA validation successful"},
            status=status.HTTP_200_OK,
        )
