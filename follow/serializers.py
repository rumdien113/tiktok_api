from rest_framework import serializers
from .models import Follow
from user.models import User
from user.serializers import UserSerializer


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']
        read_only_fields = ['follower']
    
    def create(self, validated_data):
        # Gán người tạo request là follower
        validated_data['follower'] = self.context['request'].user
        return super().create(validated_data)


class FollowUserSerializer(serializers.ModelSerializer):
    """Serializer hiển thị thông tin của user được follow hoặc follower"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firstname', 'lastname', 'avatar']


class FollowerListSerializer(serializers.ModelSerializer):
    """Serializer để hiển thị danh sách người theo dõi mình"""
    follower = FollowUserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'created_at']


class FollowingListSerializer(serializers.ModelSerializer):
    """Serializer để hiển thị danh sách người mình đang theo dõi"""
    followed = FollowUserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'followed', 'created_at']
