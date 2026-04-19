from rest_framework import viewsets, permissions
from .models import Channel, Post
from .serializers import ChannelSerializer, PostSerializer

class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Channels.
    Students can view channels, but only Admins can create them via Django Admin.
    """
    queryset = Channel.objects.all().order_by('id')
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for live Posts/Messages in channels.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return the latest 50 posts for the requested channel.
        """
        queryset = Post.objects.all()
        channel_id = self.request.query_params.get('channel')
        
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
            
        return queryset[:50]

    def perform_create(self, serializer):
        """
        Auto-assign the logged-in student and award points!
        """
        post = serializer.save(author=self.request.user)
        
        # Award 1 point for participating in the community chat
        self.request.user.add_points(1)