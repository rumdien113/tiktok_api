from rest_framework import serializers
from .models import Like
from user.serializers import UserSerializer

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'target_id', 'target_type']
        read_only_fields = ['user']

class LikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['target_id', 'target_type']
    
    def validate(self, data):
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        
        # Check if target_type is valid
        if target_type not in ['post', 'comment']:
            raise serializers.ValidationError(f"Invalid target_type: {target_type}")
        
        # Check if target exists
        if target_type == 'post':
            from post.models import Post
            try:
                Post.objects.get(id=target_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError(f"Post with id {target_id} does not exist")
        elif target_type == 'comment':
            from comment.models import Comment
            try:
                Comment.objects.get(id=target_id)
            except Comment.DoesNotExist:
                raise serializers.ValidationError(f"Comment with id {target_id} does not exist")
        
        # Check if like already exists
        user = self.context['request'].user
        if Like.objects.filter(user=user, target_id=target_id, target_type=target_type).exists():
            raise serializers.ValidationError("You've already liked this item")
            
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        like = Like.objects.create(
            user=user,
            target_id=validated_data['target_id'],
            target_type=validated_data['target_type']
        )
        return like
