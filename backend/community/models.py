from django.db import models
from django.conf import settings

class Channel(models.Model):
    """
    Chat rooms for the community (e.g., #general, #math-help)
    """
    name = models.CharField(max_length=100, unique=True, help_text="e.g., General, Math-Help")
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name.lower()}"

class Post(models.Model):
    """
    Live messages sent within a specific channel
    """
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Return newest posts first
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return f"{self.author.username} in {self.channel.name}"