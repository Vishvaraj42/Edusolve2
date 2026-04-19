from rest_framework import serializers
from .models import PracticeQuestion, StudentAnswer
from doubts.serializers import DoubtSessionSerializer


class PracticeQuestionSerializer(serializers.ModelSerializer):
    """Serializer for PracticeQuestion model"""
    related_session_detail = DoubtSessionSerializer(
        source='related_session',
        read_only=True
    )
    accuracy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = PracticeQuestion
        fields = [
            'id',
            'related_session',
            'related_session_detail',
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_answer',
            'explanation',
            'difficulty',
            'topic',
            'created_at',
            'times_attempted',
            'times_correct',
            'accuracy_rate',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'times_attempted',
            'times_correct',
            'accuracy_rate'
        ]


class PracticeQuestionListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view (no correct answer!)"""
    accuracy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = PracticeQuestion
        fields = [
            'id',
            'related_session',
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'difficulty',
            'topic',
            'times_attempted',
            'accuracy_rate',
        ]
        # Notice: correct_answer and explanation are hidden!


class SubmitAnswerSerializer(serializers.ModelSerializer):
    """Serializer for submitting an answer"""
    
    class Meta:
        model = StudentAnswer
        fields = [
            'question',
            'selected_answer',
            'time_taken_seconds',
        ]


class StudentAnswerSerializer(serializers.ModelSerializer):
    """Serializer for viewing student answers"""
    question_detail = PracticeQuestionSerializer(
        source='question',
        read_only=True
    )
    
    class Meta:
        model = StudentAnswer
        fields = [
            'id',
            'student',
            'question',
            'question_detail',
            'selected_answer',
            'is_correct',
            'time_taken_seconds',
            'attempted_at',
        ]
        read_only_fields = ['id', 'student', 'is_correct', 'attempted_at']