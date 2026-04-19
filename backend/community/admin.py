from django.contrib import admin
from .models import Channel, Post

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin interface for Community Channels"""
    
    list_display = [
        'name', 
        'description', 
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'description'
    ]
    
    readonly_fields = [
        'created_at'
    ]
    
    ordering = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Community Posts/Messages"""
    
    list_display = [
        'author', 
        'channel', 
        'content_preview',
        'created_at'
    ]
    
    list_filter = [
        'channel', 
        'created_at'
    ]
    
    search_fields = [
        'content', 
        'author__username', 
        'channel__name'
    ]
    
    readonly_fields = ['created_at']
    
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Show first 50 characters of the message"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Message Preview'