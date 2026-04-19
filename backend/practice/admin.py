from django.contrib import admin
from .models import PracticeQuestion, StudentAnswer


@admin.register(PracticeQuestion)
class PracticeQuestionAdmin(admin.ModelAdmin):
    """Simple admin for PracticeQuestion"""
    
    list_display = ['question_preview', 'difficulty', 'times_attempted', 'accuracy_rate']
    list_filter = ['difficulty', 'related_session__subject']
    search_fields = ['question_text', 'topic']
    
    def question_preview(self, obj):
        """Show first 50 characters of question"""
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    
    question_preview.short_description = 'Question'


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    """Simple admin for StudentAnswer"""
    
    list_display = ['student', 'question', 'is_correct', 'attempted_at']
    list_filter = ['is_correct', 'attempted_at']
    search_fields = ['student__username']
