from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DoubtSessionViewSet,
    ChatMessageViewSet,
    StudentDoubtStatsView,
)

# Create router - Hitesh teaches this!
# Router automatically creates URLs for ViewSets
router = DefaultRouter()
router.register(r'sessions', DoubtSessionViewSet, basename='doubt-session')
router.register(r'messages', ChatMessageViewSet, basename='chat-message')
router.register(r'stats', StudentDoubtStatsView, basename='doubt-stats')

app_name = 'doubts'

urlpatterns = [
    path('', include(router.urls)),
]