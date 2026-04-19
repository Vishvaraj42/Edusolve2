from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(AbstractUser):
    """
    Custom user model for students
    Extends Django's AbstractUser to add student-specific fields
    
    Just like Hitesh teaches - we inherit from AbstractUser to get
    all the built-in user functionality (username, password, email, etc.)
    and add our own fields on top!
    """
    
    # Choices - just like Hitesh showed in his models video
    GRADE_CHOICES = [
        (9, '9th Grade'),
        (10, '10th Grade'),
    ]
    
    # Basic Info - these are our custom fields
    grade = models.IntegerField(
    choices=GRADE_CHOICES,
    validators=[MinValueValidator(9), MaxValueValidator(10)],
    help_text="Student's current grade (9th or 10th)",
    null=True,      
    blank=True  
)
    
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Optional contact number"
    )
    
    profile_picture = models.ImageField(
        upload_to='profiles/',  # Hitesh explains upload_to - where files go
        null=True, 
        blank=True,
        help_text="Student profile picture"
    )
    
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text="Short bio about the student"
    )
    
    # Gamification - make learning fun!
    points = models.IntegerField(
        default=0,
        help_text="Points earned from activities"
    )
    
    # Preferences - using JSONField (advanced!)
    preferred_subjects = models.JSONField(
        default=list,
        blank=True,
        help_text="List of subjects student is interested in"
    )
    
    # Timestamps - auto_now_add and auto_now (Hitesh covers this!)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['-created_at']  # Newest first
    
    def __str__(self):
        """
        String representation - Hitesh always emphasizes this!
        This is what shows in Django admin
        """
        return f"{self.username} - Grade {self.grade}"
    
    def add_points(self, points):
        """
        Custom method - just like Hitesh teaches!
        This is how we add behavior to our models
        """
        self.points += points
        self.save()