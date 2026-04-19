from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PracticeQuestionViewSet,
    StudentAnswerViewSet,
    QuizViewSet,  # Add this if you created QuizViewSet
)

router = DefaultRouter()
router.register(r'questions', PracticeQuestionViewSet, basename='practice-question')
router.register(r'answers', StudentAnswerViewSet, basename='student-answer')
router.register(r'quiz', QuizViewSet, basename='quiz')  # Add this line

urlpatterns = [
    path('', include(router.urls)),
]