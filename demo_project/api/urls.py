from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DemoViewSet

router = DefaultRouter()
router.register(r'demo', DemoViewSet, basename='demo')

urlpatterns = router.urls
