from rest_framework import serializers
from .models import DoubtSession, ChatMessage
from accounts.serializers import StudentSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage model
    """
    
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'session',
            'sender_type',
            'content',
            'image',
            'ai_model',
            'tokens_used',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp', 'ai_model', 'tokens_used']


class ChatMessageDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer with nested data
    Just like Hitesh teaches - we can nest serializers!
    """
    
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'sender_type',
            'content',
            'image',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']


class DoubtSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for DoubtSession model
    """
    student_detail = StudentSerializer(source='student', read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DoubtSession
        fields = [
            'id',
            'student',
            'student_detail',
            'subject',
            'title',
            'status',
            'created_at',
            'updated_at',
            'resolved_at',
            'message_count',
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at', 'resolved_at']
    
    def get_message_count(self, obj):
        """
        Custom method field - Hitesh covers this!
        Returns count of messages in this session
        """
        return obj.messages.count()


class DoubtSessionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer with all messages
    """
    student_detail = StudentSerializer(source='student', read_only=True)
    messages = ChatMessageDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = DoubtSession
        fields = [
            'id',
            'student',
            'student_detail',
            'subject',
            'title',
            'status',
            'created_at',
            'updated_at',
            'resolved_at',
            'messages',
        ]
        read_only_fields = ['id', 'student', 'created_at', 'updated_at', 'resolved_at']


class CreateDoubtSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new doubt session
    """
    
    class Meta:
        model = DoubtSession
        # FIX: Added 'id' to the fields list so the frontend gets the session ID back
        fields = ['id', 'subject', 'title'] 
        read_only_fields = ['id']