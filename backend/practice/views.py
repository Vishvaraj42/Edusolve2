from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Avg
from .models import PracticeQuestion, StudentAnswer
from doubts.models import DoubtSession
from .serializers import (
    PracticeQuestionSerializer,
    PracticeQuestionListSerializer,
    SubmitAnswerSerializer,
    StudentAnswerSerializer,
)
import csv
from django.http import HttpResponse


class PracticeQuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PracticeQuestion
    
    Provides CRUD operations for practice questions
    Just like Hitesh teaches - ViewSet handles everything!
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return all practice questions
        Can be filtered using query parameters
        """
        # =========================================================
        # FIX 2: PREVENT DATA LEAKAGE!
        # Only return questions from sessions that belong to THIS student
        # =========================================================
        queryset = PracticeQuestion.objects.filter(related_session__student=self.request.user)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by subject (through related session)
        subject = self.request.query_params.get('subject', None)
        if subject:
            queryset = queryset.filter(related_session__subject=subject)
        
        # Filter by session
        session_id = self.request.query_params.get('session', None)
        if session_id:
            queryset = queryset.filter(related_session_id=session_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Use different serializers for list vs detail
        """
        if self.action == 'list':
            return PracticeQuestionListSerializer
        return PracticeQuestionSerializer
    
    @action(detail=False, methods=['get'], url_path='by-session/(?P<session_id>[^/.]+)')
    def by_session(self, request, session_id=None):
        questions = self.get_queryset().filter(related_session_id=session_id)
        serializer = PracticeQuestionListSerializer(questions, many=True)
        return Response({
            'count': questions.count(),
            'session_id': session_id,
            'questions': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='by-difficulty/(?P<difficulty>[^/.]+)')
    def by_difficulty(self, request, difficulty=None):
        questions = self.get_queryset().filter(difficulty=difficulty)
        serializer = PracticeQuestionListSerializer(questions, many=True)
        return Response({
            'count': questions.count(),
            'difficulty': difficulty,
            'questions': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        question = self.get_object()
        stats = {
            'question_id': question.id,
            'total_attempts': question.times_attempted,
            'correct_attempts': question.times_correct,
            'accuracy_rate': question.accuracy_rate,
            'difficulty': question.difficulty,
        }
        return Response(stats)


class StudentAnswerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StudentAnswer
    """
    serializer_class = StudentAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return answers for current student only"""
        return StudentAnswer.objects.filter(student=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SubmitAnswerSerializer
        return StudentAnswerSerializer

    def create(self, request, *args, **kwargs):
        """
        Submit an answer - auto-grading happens here!
        Allows multiple attempts for practice.
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        selected_answer = serializer.validated_data['selected_answer']
        time_taken = serializer.validated_data.get('time_taken_seconds', None)
        
        is_correct = (selected_answer.upper() == question.correct_answer.upper())
        
        try:
            answer = StudentAnswer.objects.create(
                student=request.user,
                question=question,
                selected_answer=selected_answer.upper(),
                is_correct=is_correct,
                time_taken_seconds=time_taken
            )
            
            return Response({
                'is_correct': is_correct,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'your_answer': selected_answer
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='my-answers')
    def my_answers(self, request):
        answers = self.get_queryset().order_by('-attempted_at')
        serializer = StudentAnswerSerializer(answers, many=True)
        return Response({
            'count': answers.count(),
            'answers': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        student = request.user
        answers = self.get_queryset()
        
        total_attempts = answers.count()
        correct_answers = answers.filter(is_correct=True).count()
        accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
        
        easy_correct = answers.filter(is_correct=True, question__difficulty='easy').count()
        medium_correct = answers.filter(is_correct=True, question__difficulty='medium').count()
        hard_correct = answers.filter(is_correct=True, question__difficulty='hard').count()
        
        stats = {
            'total_attempts': total_attempts,
            'correct_answers': correct_answers,
            'wrong_answers': total_attempts - correct_answers,
            'accuracy_percentage': round(accuracy, 2),
            'total_points': student.points,
            'by_difficulty': {
                'easy': easy_correct,
                'medium': medium_correct,
                'hard': hard_correct,
            },
        }
        return Response(stats)

    @action(detail=False, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request):
        from accounts.models import Student
        top_students = Student.objects.all().order_by('-points')[:10]
        
        leaderboard = []
        for rank, student in enumerate(top_students, start=1):
            student_answers = StudentAnswer.objects.filter(student=student)
            leaderboard.append({
                'rank': rank,
                'username': student.username,
                'grade': student.grade,
                'points': student.points,
                'total_questions_answered': student_answers.count(),
                'correct_answers': student_answers.filter(is_correct=True).count(),
            })
        
        return Response({'leaderboard': leaderboard})

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        answers = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="my_answers_{request.user.username}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Question', 'Your Answer', 'Correct Answer', 'Result', 'Points', 'Date'])
        
        for answer in answers:
            points_map = {'easy': 5, 'medium': 10, 'hard': 15}
            points = points_map.get(answer.question.difficulty, 0) if answer.is_correct else 0
            writer.writerow([
                answer.question.question_text[:50] + '...',
                answer.selected_answer,
                answer.question.correct_answer,
                'Correct' if answer.is_correct else 'Wrong',
                points,
                answer.attempted_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response


class QuizViewSet(viewsets.ViewSet):
    """
    ViewSet for quiz functionality
    Generates random quizzes based on criteria
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='random')
    def random_quiz(self, request):
        count = int(request.query_params.get('count', 5))
        count = min(count, 20)
        
        difficulty = request.query_params.get('difficulty', None)
        subject = request.query_params.get('subject', None)
        
        # Use only questions related to this user!
        questions = PracticeQuestion.objects.filter(related_session__student=request.user)
        if difficulty:
            questions = questions.filter(difficulty=difficulty)
        if subject:
            questions = questions.filter(related_session__subject=subject)
        
        answered_question_ids = StudentAnswer.objects.filter(
            student=request.user
        ).values_list('question_id', flat=True)
        
        unanswered = questions.exclude(id__in=answered_question_ids)
        
        if unanswered.count() < count:
            quiz_questions = list(unanswered) + list(
                questions.filter(id__in=answered_question_ids).order_by('?')[:count - unanswered.count()]
            )
        else:
            quiz_questions = list(unanswered.order_by('?')[:count])
        
        from .serializers import PracticeQuestionListSerializer
        serializer = PracticeQuestionListSerializer(quiz_questions, many=True)
        
        return Response({
            'quiz_id': f"quiz_{request.user.id}_{count}",
            'question_count': len(quiz_questions),
            'difficulty': difficulty or 'mixed',
            'subject': subject or 'mixed',
            'questions': serializer.data,
        })