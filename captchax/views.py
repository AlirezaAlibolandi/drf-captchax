"""
Views for CAPTCHA generation and validation.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .captcha import CaptchaGenerator
from .validator import CaptchaSerializer
from .utils import image_to_base64
from .settings import CAPTCHAX_CONFIG, get_backend_class


class GenerateCaptchaView(APIView):
    """
    View for generating new CAPTCHA images.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Generate a new CAPTCHA image.
        
        Returns:
            JSON response with:
            - captcha_id: Unique identifier for the CAPTCHA
            - image: Base64 encoded CAPTCHA image
        """
        # Generate CAPTCHA
        generator = CaptchaGenerator()
        captcha_id, image = generator.generate_image()
        
        # Store CAPTCHA
        backend = get_backend_class()()
        backend.store_captcha(
            captcha_id,
            image.text,  # Access the generated text
            CAPTCHAX_CONFIG["TIMEOUT"]
        )
        
        # Convert image to base64
        image_data = image_to_base64(image)
        
        return Response({
            'captcha_id': captcha_id,
            'image': f"data:image/png;base64,{image_data}"
        })


class ValidateCaptchaView(APIView):
    """
    View for validating CAPTCHA responses.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Validate a CAPTCHA response.
        
        Expected POST data:
        - captcha_id: The CAPTCHA identifier
        - captcha_text: The user's response text
        
        Returns:
            200 OK if valid
            400 Bad Request if invalid
        """
        serializer = CaptchaSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response({'detail': 'CAPTCHA validation successful'})
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        ) 