"""
URL patterns for CAPTCHA views.
"""

from django.urls import path
from . import views

app_name = 'captchax'

urlpatterns = [
    path('generate/', views.GenerateCaptchaView.as_view(), name='generate'),
    path('validate/', views.ValidateCaptchaView.as_view(), name='validate'),
] 