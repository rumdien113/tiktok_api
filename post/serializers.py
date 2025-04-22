import uuid
from rest_framework import serializers

from user.models import User
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    id_user = serializers.CharField(write_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'id_user', 'media', 'title', 'share', 'created_at']

    def create(self, validated_data):
        user_id = validated_data.pop('id_user')

        # Kiểm tra xem user_id có phải là UUID hợp lệ hay không
        try:
            uuid.UUID(str(user_id))
        except ValueError:
            raise serializers.ValidationError({'id_user': 'Invalid UUID format'})

        # Tìm người dùng dựa trên UUID
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'id_user': 'User not found'})

        validated_data['id_user'] = user
        return Post.objects.create(**validated_data)

