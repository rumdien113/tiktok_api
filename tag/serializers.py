from rest_framework import serializers
from .models import Tag
from post_tag.models import PostTag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class TagCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

class PostTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(source='tag.name', read_only=True)

    class Meta:
        model = PostTag
        fields = ['id', 'post', 'tag', 'tag_name']
        read_only_fields = ['id', 'tag_name']

class PostTagCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTag
        fields = ['post', 'tag']

    def validate(self, data):
        post = data.get('post')
        tag = data.get('tag')
        if PostTag.objects.filter(post=post, tag=tag).exists():
            raise serializers.ValidationError("This tag is already associated with this post.")
        return data
