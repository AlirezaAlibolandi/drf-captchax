"""
Example usage of the CAPTCHA package.

This module provides example implementations for common use cases.
"""

from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from .validator import CaptchaValidator


class UserRegistrationSerializer(serializers.Serializer):
    """Example registration serializer with CAPTCHA validation."""
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    captcha_id = serializers.CharField()
    captcha_text = serializers.CharField(validators=[CaptchaValidator()])


class RegistrationViewSet(viewsets.ViewSet):
    """Example registration viewset with CAPTCHA validation."""
    
    def create(self, request):
        """Handle user registration with CAPTCHA validation."""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # CAPTCHA is valid, proceed with registration
            # Your registration logic here
            return Response({
                'detail': 'Registration successful'
            })
            
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# Example Django template usage:
"""
<form method="post" action="{% url 'register' %}">
    {% csrf_token %}
    <input type="text" name="username" required>
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    
    <!-- CAPTCHA field -->
    <img id="captcha-image" src="{% url 'captchax:generate' %}">
    <input type="hidden" name="captcha_id" id="captcha-id">
    <input type="text" name="captcha_text" required>
    
    <button type="submit">Register</button>
</form>

<script>
// JavaScript to handle CAPTCHA refresh
function refreshCaptcha() {
    fetch('{% url "captchax:generate" %}')
        .then(response => response.json())
        .then(data => {
            document.getElementById('captcha-image').src = data.image;
            document.getElementById('captcha-id').value = data.captcha_id;
        });
}

// Refresh CAPTCHA on page load
document.addEventListener('DOMContentLoaded', refreshCaptcha);
</script>
"""