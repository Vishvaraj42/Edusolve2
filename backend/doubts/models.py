from django.db import models
from django.conf import settings
from django.utils import timezone


class DoubtSession(models.Model):
    """
    Represents a doubt-solving session between student and AI
    
    This is like a conversation thread - similar to Hitesh's
    blog post example in the videos
    """
    
    # Choices for subjects
    SUBJECT_CHOICES = [
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('archived', 'Archived'),
    ]
    
    # ForeignKey - Hitesh explains this as "linking tables"
    # settings.AUTH_USER_MODEL points to our Student model
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # If student deleted, delete sessions too
        related_name='doubt_sessions',  # Access sessions from student
        help_text="The student who created this doubt session"
    )
    
    subject = models.CharField(
        max_length=20, 
        choices=SUBJECT_CHOICES,
        help_text="Subject of the doubt"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Brief description of the doubt"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Doubt Session"
        verbose_name_plural = "Doubt Sessions"
        
        # Indexes - for faster database queries (advanced!)
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['subject', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.title}"
    
    def mark_resolved(self):
        """Custom method to mark session as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
        # Award points to student
        self.student.add_points(10)


class ChatMessage(models.Model):
    """
    Individual messages in a doubt session
    
    This is a ONE-TO-MANY relationship with DoubtSession
    (One session has many messages)
    """
    
    SENDER_CHOICES = [
        ('student', 'Student'),
        ('ai', 'AI Assistant'),
    ]
    
    # ForeignKey to DoubtSession - linking messages to sessions
    session = models.ForeignKey(
        DoubtSession,
        on_delete=models.CASCADE,
        related_name='messages',  # Access messages via session.messages.all()
        help_text="The doubt session this message belongs to"
    )
    
    sender_type = models.CharField(
        max_length=10, 
        choices=SENDER_CHOICES,
        help_text="Who sent this message"
    )
    
    content = models.TextField(
        help_text="The actual message content"
    )
    
    # Optional image attachment (for diagrams, screenshots)
    image = models.ImageField(
        upload_to='doubt_images/',
        null=True,
        blank=True,
        help_text="Optional image attachment"
    )
    
    # AI metadata (for tracking)
    ai_model = models.CharField(
        max_length=50,
        blank=True,
        help_text="AI model used (e.g., claude-3-sonnet)"
    )
    
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="Tokens consumed in AI response"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']  # Chronological order
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
    
    def __str__(self):
        return f"{self.session.title} - {self.sender_type} at {self.timestamp}"