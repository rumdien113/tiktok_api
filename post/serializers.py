from rest_framework import serializers
from .models import Post
from user.serializers import UserSerializer

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'media', 'description', 'created_at', 'updated_at', 
                 'likes_count', 'comments_count', 'shares_count']
    
    def get_likes_count(self, obj):
        # Import inside method to avoid circular imports
        from likes.models import Like
        return Like.objects.filter(target_id=obj.id, target_type='post').count()
    
    def get_comments_count(self, obj):
        # Import inside method to avoid circular imports
        from comments.models import Comment
        return Comment.objects.filter(post=obj).count()
    
    def get_shares_count(self, obj):
        # Import inside method to avoid circular imports
        from shares.models import Share
        return Share.objects.filter(post=obj).count()

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['media', 'description']
    
    def create(self, validated_data):
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)
        return post
