from django.contrib import admin
from .models import DoubtSession, ChatMessage


@admin.register(DoubtSession)
class DoubtSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for DoubtSession
    
    Just like Hitesh teaches - we customize what we see and how we interact
    """
    
    list_display = [
        'title', 
        'student', 
        'subject', 
        'status', 
        'created_at',
        'resolved_at'
    ]
    
    list_filter = [
        'subject', 
        'status', 
        'created_at'
    ]
    
    search_fields = [
        'title', 
        'student__username',  # Search by student's username
        'student__email'
    ]
    
    # Read-only fields (can't edit these)
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'resolved_at'
    ]
    
    # Default ordering
    ordering = ['-created_at']
    
    # How many items per page
    list_per_page = 20
    
    # Date hierarchy for easy navigation
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage"""
    
    list_display = [
        'session', 
        'sender_type', 
        'content_preview',
        'timestamp'
    ]
    
    list_filter = [
        'sender_type', 
        'timestamp'
    ]
    
    search_fields = [
        'content', 
        'session__title'
    ]
    
    readonly_fields = ['timestamp']
    
    ordering = ['-timestamp']
    
    # Custom method to show preview of content
    def content_preview(self, obj):
        """Show first 50 characters of message"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Content'