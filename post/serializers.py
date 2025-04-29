from rest_framework import status
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import Post # Assuming your Post model is in models.py
from user.serializers import UserSerializer # Keep existing import
from ai_result.utils import process_and_upload_image, process_and_upload_video

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
        from like.models import Like
        return Like.objects.filter(target_id=obj.id, target_type='post').count()

    def get_comments_count(self, obj):
        from comment.models import Comment
        return Comment.objects.filter(post=obj).count()

    def get_shares_count(self, obj):
        from share.models import Share
        return Share.objects.filter(post=obj).count()

class PostCreateSerializer(serializers.ModelSerializer):
    media_file = serializers.FileField(write_only=True)
    description = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Post
        fields = ['description', 'media_file']

    def create(self, validated_data):
        media_file = validated_data.pop('media_file')
        description = validated_data.get('description', '')
        user = self.context['request'].user

        content_type = media_file.content_type
        if content_type.startswith('image'):
            file_type = 'image'
            process_func = process_and_upload_image
        elif content_type.startswith('video'):
            file_type = 'video'
            process_func = process_and_upload_video
        else:
            raise ValidationError("Loai file khong duoc ho tro.")


        try:
            media_url = process_func(media_file)

            post = Post.objects.create(user=user, description=description, media=media_url)
            return post

        except ValueError as e:
            raise ValidationError({'media_file': [str(e)]})
        except Exception as e:
             raise ValidationError({'non_field_errors': [f"Đã xảy ra lỗi không mong muốn trong quá trình tạo bài đăng: {e}"]})

