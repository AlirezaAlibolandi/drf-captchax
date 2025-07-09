from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from captchax.validator import CaptchaValidator


class DemoSerializer(serializers.Serializer):
    username = serializers.CharField()
    captcha_id = serializers.CharField()
    captcha_text = serializers.CharField()

    def validate(self, attrs):
        validator = CaptchaValidator()
        validator.validate(attrs['captcha_text'], attrs['captcha_id'])
        return attrs


class DemoViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = DemoSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"detail": "CAPTCHA valid"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
