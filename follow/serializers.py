from rest_framework import serializers
from .models import Follow
from user.serializers import UserSerializer

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    followed = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']

class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['followed']
    
    def validate(self, data):
        follower = self.context['request'].user
        followed = data.get('followed')
        
        # Check if user is trying to follow themselves
        if follower == followed:
            raise serializers.ValidationError("You cannot follow yourself")
        
        # Check if follow relationship already exists
        if Follow.objects.filter(follower=follower, followed=followed).exists():
            raise serializers.ValidationError("You are already following this user")
            
        return data
    
    def create(self, validated_data):
        follower = self.context['request'].user
        followed = validated_data.get('followed')
        follow = Follow.objects.create(follower=follower, followed=followed)
        return follow
