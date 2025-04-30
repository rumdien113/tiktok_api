import uuid
from rest_framework import serializers

from user.serializers import UserSerializer # Keep existing import
from post.models import Post
from user.models import User
from like.models import Like
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.CharField(write_only=True)
    parent_comment = serializers.CharField(write_only=True, required=False, allow_null=True)
    parent_comment_id = serializers.UUIDField(source='parent_comment.id', read_only=True)
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent_comment', 'parent_comment_id', 'content', 'is_liked', 'likes_count', 'create_at', 'updated_at'] # Remove 'user'

    def get_is_liked(self, obj):
        """
        Kiểm tra xem người dùng đang request đã like comment này hay chưa.
        """
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            # Kiểm tra trong bảng Like
            return Like.objects.filter(
                user=request.user,     # Người dùng hiện tại
                target_id=obj.id,      # ID của comment
                target_type='comment'  # Loại đối tượng là comment
            ).exists()
        return False # Trả về False nếu không có request hoặc người dùng chưa đăng nhập

    def get_likes_count(self, obj):
        """
        Đếm số lượng like cho comment này.
        """
        # Đếm trong bảng Like
        return Like.objects.filter(
            target_id=obj.id,     # ID của comment
            target_type='comment'  # Loại đối tượng là comment
        ).count()

    def get_object_by_id(self, model, obj_id, field_name):
        try:
            uuid.UUID(str(obj_id))
        except ValueError:
            raise serializers.ValidationError({field_name: 'Invalid UUID format'})
        
        try:
            return model.objects.get(id=obj_id)
        except model.DoesNotExist:
            raise serializers.ValidationError({field_name: f'{model.__name__} not found'})

    def create(self, validated_data):
        # user = self.get_object_by_id(User, validated_data.pop('user'), 'u_id') # Remove this line
        post = self.get_object_by_id(Post, validated_data.pop('post'), 'post')
        
        parent_comment = validated_data.pop('parent_comment', None)
        parent_comment_obj = None

        if parent_comment:
            parent_comment_obj = self.get_object_by_id(Comment, parent_comment, 'parent_comment')

        # validated_data['user'] = user # Remove this line
        validated_data['post'] = post
        validated_data['parent_comment'] = parent_comment_obj

        return Comment.objects.create(**validated_data)
