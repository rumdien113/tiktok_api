from rest_framework import serializers
from .models import Share
from user.serializers import UserSerializer
from post.serializers import PostSerializer

class ShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'created_at']

class ShareCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['post']
    
    def validate(self, data):
        user = self.context['request'].user
        post = data.get('post')
        
        # Check if share already exists
        if Share.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("You've already shared this post")
            
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        share = Share.objects.create(user=user, **validated_data)
        return share
