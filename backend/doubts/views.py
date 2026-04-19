from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import DoubtSession, ChatMessage
from .serializers import (
    DoubtSessionSerializer,
    DoubtSessionDetailSerializer,
    CreateDoubtSessionSerializer,
    ChatMessageSerializer,
    ChatMessageDetailSerializer,
)
from .ai_service import ai_service  # AI Integration


class DoubtSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DoubtSession
    
    Provides CRUD operations for doubt sessions
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return sessions for current user only
        """
        return DoubtSession.objects.filter(student=self.request.user)
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'retrieve':
            return DoubtSessionDetailSerializer
        elif self.action == 'create':
            return CreateDoubtSessionSerializer
        return DoubtSessionSerializer
    
    def perform_create(self, serializer):
        """
        Automatically set the student to current user when creating
        """
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Custom action to mark session as resolved
        
        POST /api/doubts/{id}/resolve/
        """
        session = self.get_object()
        session.mark_resolved()
        
        serializer = self.get_serializer(session)
        return Response({
            'message': 'Session marked as resolved!',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific doubt session
        
        GET /api/doubts/{id}/messages/
        """
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageDetailSerializer(messages, many=True)
        
        return Response({
            'count': messages.count(),
            'messages': serializer.data
        })


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ChatMessage
    
    Handles sending and receiving messages with AI integration
    """
    
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter messages by session if provided
        Only show messages from user's own sessions
        """
        queryset = ChatMessage.objects.filter(
            session__student=self.request.user
        )
        
        # Filter by session if provided in query params
        session_id = self.request.query_params.get('session', None)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset.order_by('timestamp')
    
    def create(self, request, *args, **kwargs):
        """
        Send a message and get AI response
        
        POST /api/doubts/messages/
        {
            "session": 1,
            "sender_type": "student",
            "content": "What is Newton's second law?"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate that session belongs to current user
        session_id = request.data.get('session')
        session = get_object_or_404(
            DoubtSession,
            id=session_id,
            student=request.user
        )
        
        # Save student's message
        student_message = serializer.save()
        
        # ============================================
        # AI INTEGRATION - Generate AI Response
        # ============================================
        
        try:
            # Get conversation context (last 5 messages)
            previous_messages = ChatMessage.objects.filter(
                session=session
            ).order_by('-timestamp')[:5][::-1]  # Reverse to chronological
            
            # Build context for AI
            context = []
            for msg in previous_messages[:-1]:  # Exclude current message
                context.append({
                    'role': 'assistant' if msg.sender_type == 'ai' else 'user',
                    'content': msg.content
                })
            
            # Call AI service
            ai_result = ai_service.solve_doubt(
                question=student_message.content,
                subject=session.subject,
                grade=request.user.grade,
                context=context
            )
            
            if ai_result['success']:
                # Create AI response message
                ai_message = ChatMessage.objects.create(
                    session=session,
                    sender_type='ai',
                    content=ai_result['response'],
                    ai_model=ai_result.get('model', 'llama-3.3-70b'),
                    tokens_used=ai_result.get('tokens_used', 0)
                )
                
               # ==========================================================
                # NEW: Generate Practice Questions in the background!
                # ==========================================================
                try:
                    from practice.models import PracticeQuestion 
                    
                    generated_qs = ai_service.get_practice_questions(
                        ai_answer=ai_result['response'],
                        subject=session.subject,
                        grade=request.user.grade,
                        count=3
                    )
                    
                    # Save the generated questions to your database
                    if generated_qs:
                        for q_data in generated_qs:
                            PracticeQuestion.objects.create(
                                related_session=session, 
                                question_text=q_data.get('question', 'Practice Question'),
                                
                                # Now we use the actual AI generated options!
                                option_a=q_data.get('option_a', 'Option A'), 
                                option_b=q_data.get('option_b', 'Option B'),
                                option_c=q_data.get('option_c', 'Option C'),
                                option_d=q_data.get('option_d', 'Option D'),
                                correct_answer=q_data.get('correct_answer', 'A'), 
                                
                                explanation=q_data.get('explanation', 'Based on the AI explanation.'),
                                difficulty='medium', 
                                topic=session.subject
                            )
                except Exception as e:
                    print(f"Warning: Failed to auto-generate practice questions: {str(e)}")
                # ==========================================================
                
                # Return both student and AI messages
                return Response({
                    'message': 'Message sent and AI responded!',
                    'student_message': ChatMessageSerializer(student_message).data,
                    'ai_message': ChatMessageSerializer(ai_message).data,
                    'success': True
                }, status=status.HTTP_201_CREATED)
            else:
                # AI failed, return student message with error
                return Response({
                    'message': 'Message sent, but AI response failed.',
                    'student_message': ChatMessageSerializer(student_message).data,
                    'ai_error': ai_result.get('error', 'Unknown error'),
                    'success': False
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            # Catch any unexpected errors
            print(f"AI Error: {str(e)}")
            return Response({
                'message': 'Message sent, but AI encountered an error.',
                'student_message': ChatMessageSerializer(student_message).data,
                'error': str(e),
                'success': False
            }, status=status.HTTP_201_CREATED)


class StudentDoubtStatsView(viewsets.ViewSet):
    """
    View for getting student's doubt statistics
    
    GET /api/doubts/stats/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """
        Get statistics for current student
        """
        student = request.user
        sessions = DoubtSession.objects.filter(student=student)
        
        stats = {
            'total_sessions': sessions.count(),
            'active_sessions': sessions.filter(status='active').count(),
            'resolved_sessions': sessions.filter(status='resolved').count(),
            'archived_sessions': sessions.filter(status='archived').count(),
            'total_messages': ChatMessage.objects.filter(
                session__student=student
            ).count(),
            'subjects': {
                'mathematics': sessions.filter(subject='mathematics').count(),
                'physics': sessions.filter(subject='physics').count(),
                'chemistry': sessions.filter(subject='chemistry').count(),
                'biology': sessions.filter(subject='biology').count(),
            }
        }
        
        return Response(stats)