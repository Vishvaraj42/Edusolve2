from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet, PostViewSet

# Create router
router = DefaultRouter()
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'posts', PostViewSet, basename='post')

app_name = 'community'

urlpatterns = [
    path('', include(router.urls)),
]