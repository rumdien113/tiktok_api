import uuid
from rest_framework import serializers

from post.models import Post
from user.models import User

from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(write_only=True)
    post = serializers.CharField(write_only=True)
    parent_comment = serializers.CharField(write_only=True, required=False, allow_null=True)
    parent_comment_id = serializers.UUIDField(source='parent_comment.id', read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent_comment', 'parent_comment_id', 'content', 'create_at', 'updated_at']

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
        user = self.get_object_by_id(User, validated_data.pop('user'), 'u_id')
        post = self.get_object_by_id(Post, validated_data.pop('post'), 'post')
        
        parent_comment = validated_data.pop('parent_comment', None)
        parent_comment_obj = None

        if parent_comment:
            parent_comment_obj = self.get_object_by_id(Comment, parent_comment, 'parent_comment')

        validated_data['user'] = user
        validated_data['post'] = post
        validated_data['parent_comment'] = parent_comment_obj

        return Comment.objects.create(**validated_data)

