from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit objects
    
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to owner
        # Assumes the obj has an 'author' or 'student' attribute
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'student'):
            return obj.student == request.user
        
        return False


class IsStudentGrade9Or10(permissions.BasePermission):
    """
    Only allow 9th and 10th grade students
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'grade') and request.user.grade in [9, 10]


class IsThreadAuthorOrReadOnly(permissions.BasePermission):
    """
    Thread-specific permission
    Only author can edit/delete threads
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for thread author
        return obj.author == request.user


class CanModerateContent(permissions.BasePermission):
    """
    Permission for moderators
    Can pin, lock, hide threads/replies
    """
    
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser