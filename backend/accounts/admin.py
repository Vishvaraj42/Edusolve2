from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Simple admin for Student model
    """
    
    list_display = [
        'username', 
        'email', 
        'grade', 
        'points', 
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'grade', 
        'is_staff', 
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name'
    ]
    
    ordering = ['-created_at']
    
    # Make password field use the widget
    fields = [
        'username',
        'password',
        'first_name',
        'last_name',
        'email',
        'grade',
        'phone_number',
        'profile_picture',
        'bio',
        'points',
        'preferred_subjects',
        'is_active',
        'is_staff',
        'is_superuser',
    ]