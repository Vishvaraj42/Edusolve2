from rest_framework import serializers
from .models import Channel, Post

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'name', 'description', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    # Dynamically pull the author's username to display in the chat UI
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'channel', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'author_name', 'created_at']